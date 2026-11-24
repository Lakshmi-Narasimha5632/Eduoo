"""Interview orchestration service coordinating question generation, answer evaluation, and final reports."""

from __future__ import annotations

from typing import Any, Dict, List
from django.utils import timezone

from .ai import InterviewAIService
from .evaluator import InterviewAnswerEvaluator
from .models import InterviewAnswer, InterviewChatMessage, InterviewQuestion, MockInterview
from .question_generator import InterviewQuestionGenerator


class MockInterviewService:
    @staticmethod
    def start_interview(
        user,
        target_role: str | None = None,
        interview_type: str = "technical",
        difficulty: str = "intermediate",
        duration_minutes: int = 30,
        num_questions: int = 5,
        agent_persona: str = "alex_architect",
        agent_strictness: str = "balanced",
    ) -> MockInterview:
        role = target_role or user.target_role or "Software Developer"
        interview = MockInterview.objects.create(
            user=user,
            target_role=role,
            interview_type=interview_type,
            difficulty=difficulty,
            duration_minutes=duration_minutes,
            num_questions=num_questions,
            agent_persona=agent_persona,
            agent_strictness=agent_strictness,
            status="in_progress",
        )

        # Generate Question 1
        q1_data = InterviewQuestionGenerator.generate_question(interview, order=1)
        q1_obj = InterviewQuestion.objects.create(
            interview=interview,
            question=q1_data["question"],
            category=q1_data.get("category", "technical"),
            difficulty=q1_data.get("difficulty", difficulty),
            order=1,
            expected_answer=q1_data.get("expected_answer"),
        )

        # Seed Chatbot Welcome Greeting & Opening Question
        agent = interview.agent_details
        user_name = user.first_name or user.username or "Candidate"
        greeting = (
            f"Hello {user_name}! I'm {agent['name']}, {agent['title']} at {agent['company']}. "
            f"I'll be conducting your {interview_type} mock interview for the {role} position today. "
            f"I'm looking for clear technical reasoning, system intuition, and communication. "
            f"Feel free to ask me for clarifications, hints, or discuss trade-offs as we go. Let's begin!"
        )
        InterviewChatMessage.objects.create(
            interview=interview,
            sender="agent",
            message_type="greeting",
            content=greeting,
            meta_info={"agent_name": agent["name"], "title": agent["title"], "company": agent["company"]},
        )
        InterviewChatMessage.objects.create(
            interview=interview,
            sender="agent",
            message_type="question",
            content=f"Question 1: {q1_obj.question}",
            meta_info={
                "question_id": q1_obj.id,
                "order": 1,
                "category": q1_obj.category,
                "difficulty": q1_obj.difficulty,
            },
        )
        return interview

    @staticmethod
    def agent_interaction(
        interview: MockInterview,
        interaction_type: str = "hint",
        message: str = "",
        question_text: str = "",
    ) -> Dict[str, Any]:
        agent = interview.agent_details
        q_text = question_text
        if not q_text:
            current_q = interview.questions.filter(answer_record__isnull=True).order_by("order").first()
            if current_q:
                q_text = current_q.question

        # Try live AI if available
        if InterviewAIService.is_live_ai_available():
            prompt = f"""
            You are {agent['name']}, {agent['title']} at {agent['company']}.
            Interview Context: {interview.interview_type} mock interview for role: {interview.target_role}.
            Strictness Bar: {interview.agent_strictness}.
            Current Question: {q_text}
            Candidate Interaction Request ({interaction_type}): "{message or 'Please give guidance on how to tackle this question.'}"

            Respond in first-person as {agent['name']}. Keep it natural, direct, and under 3-4 sentences.
            If they asked for a hint, give an intuitive architectural or invariant nudge without spoon-feeding the final answer.
            If they asked for clarification, state reasonable production constraints and tell them to proceed with confidence.
            """
            try:
                system_prompt = f"You are AI Interviewer {agent['name']}, embodying a {agent['style']} style at {agent['company']}."
                response_text = InterviewAIService.generate_text(prompt, system_prompt=system_prompt)
                if response_text and len(response_text.strip()) > 10:
                    reply = response_text.strip()
                    if message:
                        InterviewChatMessage.objects.create(
                            interview=interview,
                            sender="candidate",
                            message_type=interaction_type,
                            content=message,
                        )
                    InterviewChatMessage.objects.create(
                        interview=interview,
                        sender="agent",
                        message_type=interaction_type,
                        content=reply,
                        meta_info={"interaction_type": interaction_type, "agent_name": agent["name"]},
                    )
                    return {
                        "agent": agent,
                        "interaction_type": interaction_type,
                        "agent_response": reply,
                        "timestamp": timezone.now().isoformat(),
                    }
            except Exception:
                pass

        # Deterministic rich fallback tailored to agent persona & interaction type
        persona_id = interview.agent_persona or "alex_architect"

        if interaction_type == "hint":
            if persona_id == "alex_architect":
                reply = (
                    f"Consider how you decouple ingestion from heavy persistence. Ask yourself: "
                    f"what happens if the downstream database drops or latency spikes by 10x? "
                    f"Look at asynchronous buffering or write-ahead logging."
                )
            elif persona_id == "sophia_algorithms":
                reply = (
                    f"Focus closely on the state invariants and search space. Is there an order "
                    f"or monotonicity you can exploit to reduce this from polynomial O(n^2) down to "
                    f"O(n log n) or O(n) using a hash map, monotonic stack, or two pointers?"
                )
            elif persona_id == "marcus_director":
                reply = (
                    f"Frame this through the lens of business trade-offs and accountability. "
                    f"Clearly state the initial constraint, the alternatives you considered, why your team chose "
                    f"this route, and how you quantified the outcome."
                )
            else:  # elena_fullstack
                reply = (
                    f"Look at the client boundary and data contract. Can you optimize the render tree "
                    f"with selective memoization or optimistic cache updates so user interaction stays under 16ms?"
                )
        elif interaction_type == "clarification":
            reply = (
                f"Great clarifying question. In a production setting at {agent['company']}, you can safely assume "
                f"standard cloud memory limits and a moderate network latency. State your explicit assumptions and continue!"
            )
        elif interaction_type == "rephrase":
            reply = (
                f"In simpler terms: Break this problem down into its core input, the desired output contract, "
                f"and the critical bottleneck that would cause it to fail at scale."
            )
        else:
            reply = (
                f"You are on the right track. Be concise, highlight the trade-offs, and explain how you would "
                f"test and monitor this solution in production."
            )

        if message:
            InterviewChatMessage.objects.create(
                interview=interview,
                sender="candidate",
                message_type=interaction_type,
                content=message,
            )
        InterviewChatMessage.objects.create(
            interview=interview,
            sender="agent",
            message_type=interaction_type,
            content=reply,
            meta_info={"interaction_type": interaction_type, "agent_name": agent["name"]},
        )

        return {
            "agent": agent,
            "interaction_type": interaction_type,
            "agent_response": reply,
            "timestamp": timezone.now().isoformat(),
        }

    @staticmethod
    def submit_answer(interview: MockInterview, answer_text: str) -> Dict[str, Any]:
        # Get the latest unanswered question
        current_question = interview.questions.filter(answer_record__isnull=True).order_by("order").first()
        if not current_question:
            return {"error": "All questions have been answered. Please finish the interview."}

        current_order = current_question.order
        max_questions = getattr(interview, "num_questions", 5) or 5

        # Record candidate answer message in chat history
        InterviewChatMessage.objects.create(
            interview=interview,
            sender="candidate",
            message_type="answer",
            content=answer_text,
            meta_info={"question_order": current_order, "question_id": current_question.id},
        )

        # Evaluate answer
        eval_result = InterviewAnswerEvaluator.evaluate_answer(
            question_text=current_question.question,
            answer_text=answer_text,
            target_role=interview.target_role,
            expected_answer=current_question.expected_answer,
        )

        answer_obj = InterviewAnswer.objects.create(
            question=current_question,
            answer=answer_text,
            score=eval_result["score"],
            technical_accuracy=eval_result["technical_accuracy"],
            communication_score=eval_result["communication_score"],
            relevance_score=eval_result["relevance_score"],
            confidence_score=eval_result["confidence_score"],
            feedback=eval_result["feedback"],
            strengths=eval_result["strengths"],
            weaknesses=eval_result["weaknesses"],
        )

        agent = interview.agent_details
        next_question = None

        if current_order < max_questions:
            # Build previous QA history for adaptation
            history = []
            for q in interview.questions.all():
                if hasattr(q, "answer_record"):
                    history.append({"question": q.question, "score": q.answer_record.score})

            next_q_data = InterviewQuestionGenerator.generate_question(
                interview, order=current_order + 1, previous_qa=history
            )
            next_question = InterviewQuestion.objects.create(
                interview=interview,
                question=next_q_data["question"],
                category=next_q_data.get("category", "technical"),
                difficulty=next_q_data.get("difficulty", interview.difficulty),
                order=current_order + 1,
                expected_answer=next_q_data.get("expected_answer"),
            )

            # Record Agent Feedback in Chatbot Stream
            feedback_msg = (
                f"Evaluation: {eval_result['score']}/100. {eval_result['feedback']}"
            )
            InterviewChatMessage.objects.create(
                interview=interview,
                sender="agent",
                message_type="feedback",
                content=feedback_msg,
                meta_info={
                    "score": eval_result["score"],
                    "strengths": eval_result["strengths"],
                    "weaknesses": eval_result["weaknesses"],
                },
            )

            # Post next question into Chatbot Stream
            InterviewChatMessage.objects.create(
                interview=interview,
                sender="agent",
                message_type="question",
                content=f"Question {next_question.order}: {next_question.question}",
                meta_info={
                    "question_id": next_question.id,
                    "order": next_question.order,
                    "category": next_question.category,
                    "difficulty": next_question.difficulty,
                },
            )
        else:
            # All answered, auto-finish interview
            MockInterviewService.finish_interview(interview)
            finish_msg = (
                f"Thank you for walking through your solution! Your final answer has been evaluated ({eval_result['score']}/100). "
                f"You have answered all {max_questions} questions for this round. "
                f"Click 'Finish Interview & View Scorecard' to review your comprehensive evaluation."
            )
            InterviewChatMessage.objects.create(
                interview=interview,
                sender="agent",
                message_type="feedback",
                content=finish_msg,
                meta_info={
                    "is_complete": True,
                    "score": eval_result["score"],
                    "strengths": eval_result["strengths"],
                    "weaknesses": eval_result["weaknesses"],
                },
            )

        from .serializers import InterviewChatMessageSerializer
        all_messages = InterviewChatMessageSerializer(interview.chat_messages.all(), many=True).data

        return {
            "answered_question_id": current_question.id,
            "evaluation": eval_result,
            "next_question": {
                "id": next_question.id,
                "order": next_question.order,
                "question": next_question.question,
                "question_text": next_question.question,
                "category": next_question.category,
                "difficulty": next_question.difficulty,
            } if next_question else None,
            "is_complete": current_order >= max_questions,
            "is_finished": current_order >= max_questions,
            "messages": all_messages,
        }

    @staticmethod
    def send_chat_message(
        interview: MockInterview,
        message: str,
        mode: str = "chat",
    ) -> Dict[str, Any]:
        trimmed = message.strip()
        if not trimmed:
            return {"error": "Message content cannot be empty."}

        current_question = interview.questions.filter(answer_record__isnull=True).order_by("order").first()

        # Handle hint or clarification modes explicitly
        if mode in ("hint", "clarify", "clarification"):
            interaction_type = "clarification" if "clarif" in mode else "hint"
            res = MockInterviewService.agent_interaction(
                interview=interview,
                interaction_type=interaction_type,
                message=trimmed,
                question_text=current_question.question if current_question else "",
            )
            from .serializers import InterviewChatMessageSerializer
            return {
                "agent_response": res.get("agent_response"),
                "interaction_type": interaction_type,
                "messages": InterviewChatMessageSerializer(interview.chat_messages.all(), many=True).data,
                "current_question": {
                    "id": current_question.id,
                    "order": current_question.order,
                    "question": current_question.question,
                    "category": current_question.category,
                } if current_question else None,
                "is_complete": current_question is None,
            }

        # Handle answer mode
        if mode == "answer" or not (trimmed.endswith("?") or trimmed.lower().startswith(("can you", "what if", "could you", "hint", "clarify"))):
            # Treat as answer to current question if unanswered questions exist
            if current_question:
                return MockInterviewService.submit_answer(interview, trimmed)

        # Candidate is asking a conversational or clarifying question in chat mode
        agent = interview.agent_details
        q_text = current_question.question if current_question else "System architecture & engineering fundamentals"

        # Ask AI Provider (Token Harbor) for live interviewer response
        prompt = f"""
        You are {agent['name']}, {agent['title']} at {agent['company']}.
        Role: {interview.target_role}.
        Current Interview Question under discussion: "{q_text}".
        Candidate just said / asked: "{trimmed}".

        Respond conversationally in first-person as {agent['name']} in 2-4 sentences.
        If they asked a question or clarification, answer helpfully with real-world production context from {agent['company']}.
        If they gave a thought, acknowledge it and prompt them to formulate their complete answer when ready.
        """
        system_prompt = f"You are {agent['name']}, leading a technical interview in {agent['style']} style."
        reply = ""
        try:
            if InterviewAIService.is_live_ai_available():
                live_text = InterviewAIService.generate_text(prompt, system_prompt=system_prompt)
                if live_text and len(live_text.strip()) > 8:
                    reply = live_text.strip()
        except Exception:
            pass

        if not reply:
            reply = (
                f"That's a reasonable observation. In a production environment at {agent['company']}, we definitely consider that constraint. "
                f"Proceed with your proposed design and let me know how you plan to handle potential bottlenecks."
            )

        # Record messages
        InterviewChatMessage.objects.create(
            interview=interview,
            sender="candidate",
            message_type="chat",
            content=trimmed,
        )
        InterviewChatMessage.objects.create(
            interview=interview,
            sender="agent",
            message_type="chat",
            content=reply,
            meta_info={"agent_name": agent["name"]},
        )

        from .serializers import InterviewChatMessageSerializer
        return {
            "agent_response": reply,
            "messages": InterviewChatMessageSerializer(interview.chat_messages.all(), many=True).data,
            "current_question": {
                "id": current_question.id,
                "order": current_question.order,
                "question": current_question.question,
                "category": current_question.category,
            } if current_question else None,
            "is_complete": current_question is None,
        }

    @staticmethod
    def ensure_chat_messages(interview: MockInterview) -> None:
        """Backfill chat messages for older interview records that have no chat history."""
        if interview.chat_messages.exists():
            return

        agent = interview.agent_details
        user_name = interview.user.first_name or interview.user.username or "Candidate"
        greeting = (
            f"Hello {user_name}! I'm {agent['name']}, {agent['title']} at {agent['company']}. "
            f"Welcome to your {interview.interview_type} mock interview for the {interview.target_role} position. "
            f"I'm looking forward to walking through these technical problems together. Let's begin!"
        )
        InterviewChatMessage.objects.create(
            interview=interview,
            sender="agent",
            message_type="greeting",
            content=greeting,
            created_at=interview.started_at,
        )

        for q in interview.questions.order_by("order"):
            InterviewChatMessage.objects.create(
                interview=interview,
                sender="agent",
                message_type="question",
                content=f"Question {q.order}: {q.question}",
                meta_info={"question_id": q.id, "order": q.order},
                created_at=q.created_at,
            )
            if hasattr(q, "answer_record"):
                ans = q.answer_record
                InterviewChatMessage.objects.create(
                    interview=interview,
                    sender="candidate",
                    message_type="answer",
                    content=ans.answer,
                    meta_info={"question_order": q.order, "score": ans.score},
                    created_at=ans.answered_at,
                )
                if ans.feedback:
                    InterviewChatMessage.objects.create(
                        interview=interview,
                        sender="agent",
                        message_type="feedback",
                        content=f"Feedback (Score: {ans.score}/100): {ans.feedback}",
                        meta_info={"score": ans.score},
                        created_at=ans.answered_at,
                    )

    @staticmethod
    def finish_interview(interview: MockInterview, is_abandoned: bool = False) -> MockInterview:
        answers = InterviewAnswer.objects.filter(question__interview=interview)
        total_questions = getattr(interview, "num_questions", None) or interview.questions.count() or 5
        answered_count = answers.count()

        # Bug fix: An uncompleted assessment with 0 questions answered MUST NOT receive an inflated score
        if answered_count == 0 or is_abandoned:
            interview.status = "abandoned"
            interview.completed_at = timezone.now()
            interview.overall_score = 0
            interview.save(update_fields=["status", "completed_at", "overall_score"])

            # Real-time alert for abandoned session
            try:
                from notifications.services import NotificationService
                NotificationService.create_notification(
                    user=interview.user,
                    title=f"Practice Session Incomplete: {interview.target_role}",
                    message=f"Your {interview.interview_type} mock interview for {interview.target_role} was ended before submitting answers.",
                    category="interview_reminder",
                    send_email=True,
                    action_url="http://localhost:5173/interviews",
                    action_label="Start Practice Session",
                    extra_metrics={"Status": "Incomplete", "Role": interview.target_role, "Questions Answered": "0"},
                )
            except Exception:
                pass

            return interview

        avg_score = int(sum(a.score for a in answers) / answered_count)

        interview.status = "completed"
        interview.completed_at = timezone.now()
        interview.overall_score = avg_score
        interview.save(update_fields=["status", "completed_at", "overall_score"])

        # Real-time notification & email for completed interview
        try:
            from notifications.services import NotificationService
            eval_decision = (
                "Strong Hire" if avg_score >= 85 and answered_count >= total_questions
                else "Hire" if avg_score >= 72
                else "Leaning Hire" if avg_score >= 60
                else "Needs Improvement"
            )
            NotificationService.create_notification(
                user=interview.user,
                title=f"Mock Interview Results: {interview.target_role} ({avg_score}/100)",
                message=f"Your {interview.interview_type} mock interview evaluation is ready! You scored {avg_score}/100 with decision '{eval_decision}'. Answered {answered_count}/{total_questions} questions.",
                category="interview_reminder",
                send_email=True,
                action_url=f"http://localhost:5173/interviews/result/{interview.id}",
                action_label="View Full Evaluation & Feedback",
                extra_metrics={
                    "Overall Score": f"{avg_score}%",
                    "Decision": eval_decision,
                    "Target Role": interview.target_role,
                    "Answered": f"{answered_count} / {total_questions}",
                },
            )
        except Exception:
            pass

        # Only create recommendation for genuine completed practice
        try:
            from recommendations.models import Recommendation
            Recommendation.objects.create(
                user=interview.user,
                category="interview",
                priority="high" if avg_score < 75 else "medium",
                title=f"Review {interview.target_role} Mock Interview ({avg_score}/100)",
                description=f"You completed a {interview.interview_type} mock interview ({answered_count}/{total_questions} answered) with score {avg_score}. Practice your weaker areas.",
                action="Review detailed feedback in the interview results dashboard.",
                estimated_time=20,
            )
        except Exception:
            pass

        return interview

    @staticmethod
    def get_result(interview: MockInterview) -> Dict[str, Any]:
        answers = InterviewAnswer.objects.filter(question__interview=interview)
        total_q = getattr(interview, "num_questions", None) or interview.questions.count() or 5
        answered_count = answers.count()

        if not answers.exists():
            return {
                "interview_id": interview.id,
                "target_role": interview.target_role,
                "interview_type": interview.interview_type,
                "status": "abandoned",
                "is_empty": True,
                "overall_score": 0,
                "questions_answered": 0,
                "total_questions": total_q,
                "scores": {
                    "technical_accuracy": 0,
                    "communication": 0,
                    "relevance": 0,
                    "confidence": 0,
                },
                "technical_score": 0,
                "communication_score": 0,
                "relevance_score": 0,
                "confidence_score": 0,
                "decision": "Incomplete / Abandoned",
                "message": "This assessment was ended with 0 questions answered. No score is awarded.",
                "strengths": [],
                "weaknesses": ["Session ended prematurely before submitting any answers."],
                "recommended_next_step": f"Start a fresh practice session for {interview.target_role} and submit full responses.",
                "answers": [],
            }

        tech_avg = int(sum(a.technical_accuracy for a in answers) / answered_count)
        comm_avg = int(sum(a.communication_score for a in answers) / answered_count)
        rel_avg = int(sum(a.relevance_score for a in answers) / answered_count)
        conf_avg = int(sum(a.confidence_score for a in answers) / answered_count)
        overall = interview.overall_score if (interview.overall_score is not None and interview.overall_score > 0) else int((tech_avg + comm_avg + rel_avg + conf_avg) / 4)

        all_strengths = []
        all_weaknesses = []
        qa_breakdown = []

        for a in answers:
            all_strengths.extend(a.strengths)
            all_weaknesses.extend(a.weaknesses)
            qa_breakdown.append({
                "order": a.question.order,
                "question": a.question.question,
                "question_text": a.question.question,
                "answer": a.answer,
                "answer_text": a.answer,
                "score": a.score,
                "technical_accuracy": a.technical_accuracy,
                "communication_score": a.communication_score,
                "relevance_score": a.relevance_score,
                "confidence_score": a.confidence_score,
                "feedback": a.feedback,
                "strengths": a.strengths,
                "weaknesses": a.weaknesses,
            })

        decision = (
            "Strong Hire" if overall >= 85 and answered_count >= total_q
            else "Hire" if overall >= 72 and answered_count >= min(3, total_q)
            else "Leaning Hire" if overall >= 60 and answered_count >= min(2, total_q)
            else "Needs Improvement" if answered_count >= 1
            else "Incomplete"
        )

        return {
            "interview_id": interview.id,
            "target_role": interview.target_role,
            "interview_type": interview.interview_type,
            "status": interview.status,
            "is_empty": False,
            "overall_score": overall,
            "questions_answered": answered_count,
            "total_questions": total_q,
            "scores": {
                "technical_accuracy": tech_avg,
                "communication": comm_avg,
                "relevance": rel_avg,
                "confidence": conf_avg,
            },
            "technical_score": tech_avg,
            "communication_score": comm_avg,
            "relevance_score": rel_avg,
            "confidence_score": conf_avg,
            "decision": decision,
            "agent_details": interview.agent_details,
            "agent_persona": interview.agent_persona,
            "agent_strictness": interview.agent_strictness,
            "agent_assessment": f"Evaluated and signed off by {interview.agent_details.get('name', 'Alex Chen')} ({interview.agent_details.get('title', 'Staff Interviewer')}) for {interview.target_role}",
            "strengths": list(dict.fromkeys(all_strengths))[:4] or [f"Formulated and defended technical solutions across {answered_count} interview questions."],
            "weaknesses": list(dict.fromkeys(all_weaknesses))[:4] or [f"Deepen architectural failure-mode analysis for {interview.target_role} questions."],
            "recommended_next_step": f"Focus practice on {interview.target_role} system architecture and edge cases." if overall < 80 else f"Target high-concurrency distributed design rounds for senior {interview.target_role} roles.",
            "answers": qa_breakdown,
        }
