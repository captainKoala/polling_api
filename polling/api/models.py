from django.db import models


class Polling(models.Model):
    """Опрос."""
    title = models.CharField(
        verbose_name='Название опроса',
        help_text='Введите название опроса',
        max_length=256,
    )
    start_date = models.DateField(
        verbose_name='Дата начала опроса',
        help_text='Введите дату начала опроса',
    )
    end_date = models.DateField(
        verbose_name='Дата окончания опроса',
        help_text='Введите дату окончания опроса',
    )
    description = models.TextField(
        verbose_name='Описание опроса',
        help_text='Введите описание для опроса',
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'


class Question(models.Model):
    """Вопрос для опроса."""
    TEXT_ANSWER = 1
    SINGLE_CHOICE = 2
    MULTIPLE_CHOICE = 3
    REQUIRE_OPTIONS = (SINGLE_CHOICE, MULTIPLE_CHOICE)
    QUESTION_TYPES_CHOICES = {
        (TEXT_ANSWER, 'Текстовый ответ'),
        (SINGLE_CHOICE, 'Ответ с выбором одного варианта'),
        (MULTIPLE_CHOICE, 'Ответ с выбором нескольких вариантов'),
    }
    text = models.TextField(
        verbose_name='Текст вопроса',
        help_text='Введите текст вопроса',
    )
    question_type = models.PositiveIntegerField(
        verbose_name='Тип вопроса',
        help_text='Выберите тип вопроса',
        choices=QUESTION_TYPES_CHOICES,
    )
    polling = models.ForeignKey(
        Polling,
        verbose_name='Опрос',
        help_text='Выберите опрос, к которому относится данный вопрос',
        related_name='questions',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text[:64]

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class QuestionOption(models.Model):
    """Вариант ответа на вопрос."""
    text = models.TextField(
        verbose_name='Текст варианта ответа',
        help_text='Введите текст варианта ответа',
    )
    question = models.ForeignKey(
        Question,
        verbose_name='Вариант ответа на вопрос',
        help_text='Введите вариант ответа на вопрос',
        related_name='options',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text[:64]

    class Meta:
        verbose_name = 'Вариант ответа на вопрос'
        verbose_name_plural = 'Варианты ответа на вопрос'


class TextAnswer(models.Model):
    """Текстовый ответ на вопрос."""
    respondent_id = models.PositiveIntegerField(
        verbose_name='Идентификатор респондента',
        help_text='Введите идентификатор респондента',
    )
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        help_text='Выберите вопрос',
        related_name='text_answers',
        on_delete=models.CASCADE,
    )
    answer = models.CharField(
        verbose_name='Ответ на вопрос',
        help_text='Введите ответ на вопрос',
        max_length=256,
    )

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name = 'Текстовый ответ'
        verbose_name_plural = 'Текстовые ответы'
        unique_together = ('respondent_id', 'question')


class ChoiceAnswer(models.Model):
    """Ответ на вопрос с выбором ответа."""
    respondent_id = models.PositiveIntegerField(
        verbose_name='Идентификатор респондента',
        help_text='Введите идентификатор респондента',
    )
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        help_text='Выберите вопрос',
        related_name='choice_answers',
        on_delete=models.CASCADE,
    )
    answer = models.ForeignKey(
        QuestionOption,
        verbose_name='Ответ на вопрос',
        help_text='Выберите вариант ответа',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.answer)

    class Meta:
        verbose_name = 'Ответ с вариантами выбора'
        verbose_name_plural = 'Ответы с вариантами выбора'
