from datetime import datetime

from rest_framework import serializers

from . import models


class QuestionOptionSerializer(serializers.ModelSerializer):
    """Сериализация для вариантов ответа."""

    class Meta:
        model = models.QuestionOption
        fields = ('id', 'text', )


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализация для вопроса."""
    options = QuestionOptionSerializer(many=True)

    class Meta:
        model = models.Question
        fields = ('id', 'text', 'question_type', 'polling', 'options')

    def validate(self, attrs):
        question_type = attrs.get('question_type')
        options = attrs.get('options')
        options_required = question_type in models.Question.REQUIRE_OPTIONS

        if options_required and not options:
            raise serializers.ValidationError(
                {'options': 'Для указанного типа вопроса должны быть переданы '
                            'варианты ответа.'})
        if options_required and len(options) < 2:
            raise serializers.ValidationError(
                {'options': 'Должны быть переданы хотя бы 2 варианта ответа.'}
            )
        return attrs

    def create(self, validated_data):
        option_texts = validated_data.pop('options')
        question = models.Question.objects.create(**validated_data)
        if validated_data['question_type'] in (models.Question.SINGLE_CHOICE,
                                               models.Question.MULTIPLE_CHOICE):
            options = [models.QuestionOption(text=opt['text'],
                                             question=question)
                       for opt in option_texts]
            models.QuestionOption.objects.bulk_create(options)
        return question

    def update(self, instance, validated_data):
        if instance.question_type in (models.Question.SINGLE_CHOICE,
                                      models.Question.MULTIPLE_CHOICE):
            models.QuestionOption.objects.filter(question=instance).delete()

        instance.text = validated_data.get('text')
        instance.type = validated_data.get('question_type')
        if instance.question_type in (models.Question.SINGLE_CHOICE,
                                      models.Question.MULTIPLE_CHOICE):
            options = validated_data.pop('options')
            new_options = [models.QuestionOption(question=instance,
                                                 text=o['text'])
                           for o in options]
            models.QuestionOption.objects.bulk_create(new_options)
        return instance


class PollingSerializer(serializers.ModelSerializer):
    """Сериализация для опроса."""
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = models.Polling
        fields = ('id', 'title', 'start_date', 'end_date', 'description',
                  'questions')
        depth = 1

    def validate(self, attrs):
        attrs = super().validate(attrs)

        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date < datetime.now().date():
            raise serializers.ValidationError(
                'Дата начала опроса не может быть меньше текущей.')
        if end_date < start_date:
            raise serializers.ValidationError(
                'Дата окончания опроса должна быть больше или равна '
                'дате его начала.')
        return attrs


class TextAnswerSerializer(serializers.ModelSerializer):
    """Сериализация текстового ответа на вопрос."""
    class Meta:
        model = models.TextAnswer
        fields = ('respondent_id', 'question', 'answer')
    #
    # def validate(self, attrs):
    #     attrs = super().validate(attrs)
    #     question, answer = attrs['question'], attrs['answer']
    #     # print(question, answer)
    #     # Если вопрос с выбором одного варианта ответа, проверяется, что
    #     # id варианта соответствует вопросу
    #     if attrs['question'].question_type == models.Question.SINGLE_CHOICE:
    #         try:
    #             option = models.QuestionOption.objects.get(id=int(answer))
    #         except (models.QuestionOption.DoesNotExist, ValueError):
    #             raise serializers.ValidationError(
    #                 {'answer': 'Неверный id варианта ответа'})
    #         if option not in question.options.all():
    #             raise serializers.ValidationError(
    #                 {'answer': 'Неверный id варианта ответа'})
    #         attrs['answer'] = str(option.id)
    #     elif question.question_type == models.Question.MULTIPLE_CHOICE:
    #         options = []
    #     return attrs


class ChoiceAnswerSerializer(serializers.ModelSerializer):
    """Сериализация ответа на вопрос с вариантами выбора."""
    class Meta:
        model = models.ChoiceAnswer
        fields = ('respondent_id', 'question', 'answer')
