from datetime import datetime

from django.db import IntegrityError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from . import models, serializers
from .permissions import ReadOnly


class PollingViewSet(viewsets.ModelViewSet):
    """Список всех опросов."""
    queryset = models.Polling.objects.all()
    serializer_class = serializers.PollingSerializer
    permission_classes = [ReadOnly | permissions.IsAdminUser]


class ActivePollingViewSet(viewsets.ReadOnlyModelViewSet):
    """Активные опросы."""
    serializer_class = serializers.PollingSerializer

    def get_queryset(self):
        today = datetime.now().date()
        return models.Polling.objects.filter(end_date__gte=today)


class QuestionViewSet(viewsets.ModelViewSet):
    """Вопросы."""
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    permission_classes = [ReadOnly | permissions.IsAdminUser]


@api_view(['POST'])
def post_answers(request):
    """Ответы на вопросы опроса."""
    data = request.data
    try:
        polling = models.Polling.objects.get(id=data['polling'])
    except KeyError:
        raise ValidationError({'polling': 'Обязательное поле'})
    except models.Polling.DoesNotExist:
        raise ValidationError(
            {'polling': 'Не найден опрос с указанным id.'})

    # Проверяется, что имеются ответы на все вопросы опроса
    expected_questions = {q.id for q in polling.questions.all()}
    try:
        actual_questions = {q['question'] for q in data['answers']}
    except KeyError:
        raise ValidationError(
            {'answers': 'Каждый ответ должен быть dict, '
                        "содержащий ключи 'answer' и 'question'"})
    if not actual_questions >= expected_questions:
        raise ValidationError(
            {'answers': 'Ожидаются ответы на вопросы с идентификаторами: '
                        f'{expected_questions}'})
    try:
        text_answers = []
        choice_answers = []
        respondent_id = data['respondent_id']
        for answer in data['answers']:
            question_id, answer = answer['question'], answer['answer']
            question = models.Question.objects.get(id=question_id)
            if question.question_type == models.Question.TEXT_ANSWER:
                text_answers.append({'question': question_id,
                                     'respondent_id': respondent_id,
                                     'answer': answer})
            elif question.question_type == models.Question.SINGLE_CHOICE:
                choice_answers.append({
                    'question': question_id,
                    'respondent_id': respondent_id,
                    'answer': answer})
            elif question.question_type == models.Question.MULTIPLE_CHOICE:
                for item in answer:
                    choice_answers.append({
                        'question': question_id,
                        'respondent_id': respondent_id,
                        'answer': item})

        text_answers_ser = serializers.TextAnswerSerializer(
            data=text_answers, many=True)
        text_answers_ser.is_valid(raise_exception=True)
        choice_answers_ser = serializers.ChoiceAnswerSerializer(
            data=choice_answers, many=True)
        choice_answers_ser.is_valid(raise_exception=True)

        text_answers_ser.save()
        choice_answers_ser.save()
    except KeyError:
        raise ValidationError({'answers': 'Каждый ответ должен содержать '
                                          "ключ 'answer'"})
    except TypeError:
        raise ValidationError(
            {'answers': 'Проверьте, что ответ на текстовый вопрос - тип '
                        'str, на вопрос с выбором 1 варианта ответа - int,'
                        ' на вопрос с выбором нескольких ответов - list'})
    except IntegrityError as e:
        raise ValidationError({'detail': str(e)})
    return Response({'detail': 'Ответы успешно приняты'},
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
def user_stat(request, user_id):
    """Статистика ответов пользователя по всем опросам."""
    text_answers = (models.TextAnswer.objects.filter(respondent_id=user_id)
                    .order_by('question__polling'))
    choice_answers = (models.ChoiceAnswer.objects.filter(respondent_id=user_id)
                      .order_by('question__polling'))
    result = {}

    for a in text_answers:
        polling_id = a.question.polling.id
        answer = {'question': a.question.id, 'answer': a.answer}
        if polling_id in result:
            result[polling_id].append(answer)
        else:
            result[polling_id] = [answer]

    for a in choice_answers:
        polling_id = a.question.polling.id
        answer = {'question': a.question.id,
                  'answer': {'id': a.answer.id, 'text': a.answer.text}}
        if polling_id in result:
            result[polling_id].append(answer)
        else:
            result[polling_id] = [answer]
    return Response(result, status=status.HTTP_200_OK)
