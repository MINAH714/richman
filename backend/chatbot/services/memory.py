from chatbot.models import ChatSession


def get_recent_messages(session, limit=6):
    """
    최근 대화 limit개를 OpenAI/GMS messages 형식으로 변환
    """

    recent_messages = (
        session.messages
        .order_by("-created_at")[:limit]
    )

    recent_messages = reversed(recent_messages)

    result = []

    for msg in recent_messages:
        result.append({
            "role": msg.role,
            "content": msg.content,
        })

    return result

def extract_recent_stock_symbols(session, limit=10):
    """
    최근 대화에서 등장한 ticker를 추출
    """

    messages = (
        session.messages
        .filter(intent_type='stock')
        .order_by('-created_at')[:limit]
    )

    result = []

    for msg in reversed(messages):
        text = msg.content.upper()

        if "삼성전자" in text:
            result.append("005930.KS")

        if "애플" in text:
            result.append("AAPL")

        if "SK하이닉스" in text:
            result.append("000660.KS")

    return list(dict.fromkeys(result))