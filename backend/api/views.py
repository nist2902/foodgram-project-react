import django_filters.rest_framework
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import (CustomUser, Favorites, Follow, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingList, Tag)
from .permissions import IsAuthor
from .serializers import (AddFavouriteRecipeSerializer, CreateRecipeSerializer,
                          IngredientSerializer, ListRecipeSerializer,
                          ShowFollowersSerializer, TagSerializer,
                          UserSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_class = RecipeFilter

    def get_permissions(self):
        if self.action == 'create':
            return IsAuthenticated(),
        if self.action in ['destroy', 'update', 'partial_update']:
            return IsAuthor(),
        return AllowAny(),

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ListRecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def showfollows(request):
    users = request.user.followers.all()
    user_obj = []
    for follow_obj in users:
        user_obj.append(follow_obj.author)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(user_obj, request)
    serializer = ShowFollowersSerializer(
        result_page, many=True, context={'current_user': request.user})
    return paginator.get_paginated_response(serializer.data)


class FollowViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, user_id):
        user = request.user
        author = get_object_or_404(CustomUser, id=user_id)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response(
                'Вы уже подписаны',
                status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=user, author=author)
        serializer = UserSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        author = CustomUser.objects.get(id=user_id)
        try:
            follow = Follow.objects.get(user=user, author=author)
            follow.delete()
            return Response('Удалено',
                            status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response('Подписки не было',
                            status=status.HTTP_400_BAD_REQUEST)


class FavouriteViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                'Вы уже добавили рецепт в избранное',
                status=status.HTTP_400_BAD_REQUEST)
        Favorites.objects.create(user=user, recipe=recipe)
        serializer = AddFavouriteRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite_obj = Favorites.objects.get(user=user, recipe=recipe)
        if not favorite_obj:
            return Response(
                'Рецепт не был в избранном',
                status=status.HTTP_400_BAD_REQUEST)
        favorite_obj.delete()
        return Response(
            'Удалено', status=status.HTTP_204_NO_CONTENT)


class ShoppingListViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                'Вы уже добавили рецепт в список покупок',
                status=status.HTTP_400_BAD_REQUEST)
        ShoppingList.objects.create(user=user, recipe=recipe)
        serializer = AddFavouriteRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_list_obj = ShoppingList.objects.get(user=user, recipe=recipe)
        if not shopping_list_obj:
            return Response(
                'Рецепт не был в списке покупок',
                status=status.HTTP_400_BAD_REQUEST)
        shopping_list_obj.delete()
        return Response(
            'Удалено', status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        shopping_cart = user.purchases.all()
        buying_list = {}
        for record in shopping_cart:
            recipe = record.recipe
            ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in buying_list:
                    buying_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    buying_list[name]['amount'] = (buying_list[name]['amount']
                                                   + amount)

        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["amount"]} '
                            f'{buying_list[item]["measurement_unit"]} \n')
        wishlist.append('\n')
        wishlist.append('FoodGram, 2021')
        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
