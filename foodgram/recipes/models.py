from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    title = models.CharField(
        verbose_name='Название',
        max_length=150
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        null=True,
        blank=False,
        upload_to='images/'
    )
    description = models.TextField(
        verbose_name='описание',
        blank=False
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты',
        through='Amount',
        through_fields=('recipe',
                        'ingredient')
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1,
        blank=False,
        validators=[MinValueValidator(1)]
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return (f'{self.author} - {self.title}')


class Ingredient(models.Model):
    title = models.CharField(
        verbose_name='Ингредиент',
        max_length=128,
        unique=True,
        db_index=True
    )
    dimension = models.CharField(
        verbose_name='Единица измерения',
        max_length=32
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'dimension'],
                name='unique_recipe_ingredient'
            )
        ]
        ordering = ['title', ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.title} {self.dimension}'


class Amount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipe_amounts',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient_amounts',
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return self.ingredient.title


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        max_length=100,
        null=True
    )
    value = models.CharField(
        verbose_name='значение тега',
        max_length=100,
        null=True
    )
    style = models.CharField(
        verbose_name='Цвет тега',
        max_length=50,
        null=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.value


class ShopList(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shoplist',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shoplist',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoplist'
            )
        ]
        verbose_name = 'Список для покупки'
        verbose_name_plural = 'Списки для покупок'

    def __str__(self):
        return self.recipe.title


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        related_name='favorite_recipe',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='UniqueFavorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return self.recipe.title


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} является подписчиком {self.author}'
