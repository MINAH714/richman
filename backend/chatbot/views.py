from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .services.chatbot import (
    classify_intent,
    handle_crypto_intent,
    handle_stock_intent,
    handle_consumption_intent,
    handle_mixed_intent,
)


class ChatSessionListView(APIView):
    """채팅 세션 목록 조회 + 생성"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user)
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatMessageView(APIView):
    """메시지 전송 + intent 분류 + 응답 생성"""
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"detail": "세션을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChatMessageSerializer(session.messages.all(), many=True)
        return Response(serializer.data)

    def post(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"detail": "세션을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user_content = request.data.get("content", "").strip()
        if not user_content:
            return Response({"detail": "메시지 내용이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 1) 사용자 메시지 저장
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=user_content,
        )

        # 2) Intent 분류
        intent_result = classify_intent(user_content)
        intent = intent_result.get("intent", "mixed")
        sub_data = intent_result.get("sub_data", {})

        # 3) Intent별 처리
        if intent == "crypto":
            result = handle_crypto_intent(user_content, sub_data)

        elif intent == "price_alert":
            coin_symbol = sub_data.get("coin_symbol")
            target_price = sub_data.get("target_price")
            direction = sub_data.get("direction", "above")

            if coin_symbol and target_price:
                try:
                    from crypto.models import PriceAlert
                    PriceAlert.objects.create(
                        user=request.user,
                        coin_symbol=coin_symbol.upper(),
                        target_price=target_price,
                        direction=direction,
                        is_active=True,
                    )
                    answer = f"✅ {coin_symbol.upper()} 가격이 {int(target_price):,}원 {'이상' if direction == 'above' else '이하'}이 되면 알려드릴게요!"
                except Exception as e:
                    answer = "가격 알림 등록 중 오류가 발생했어요."
            else:
                answer = "알림을 설정하려면 코인명과 목표 가격을 알려주세요.\n예: '비트코인 1억 되면 알려줘'"
            result = {"answer": answer}

        elif intent == "stock":
            result = handle_stock_intent(user_content, sub_data)

        elif intent == "consumption":
            result = handle_consumption_intent(user_content, sub_data)

        else:
            result = handle_mixed_intent(user_content)

        # 4) 어시스턴트 메시지 저장
        assistant_msg = ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=result.get("answer", ""),
            intent_type=intent,
        )

        return Response({
            "message": ChatMessageSerializer(assistant_msg).data,
            "intent": intent,
            "sub_data": sub_data,
            "context_data": result.get("context_data", {}),
        }, status=status.HTTP_201_CREATED)