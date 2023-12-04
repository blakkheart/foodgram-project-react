from django.contrib import admin
from django.contrib.auth import get_user_model

from recipe.models import ReciepeShopList, RecipeFavourite
from user.models import UserFollowing

User = get_user_model()


class ReciepeShopListInline(admin.TabularInline):
    model = ReciepeShopList
    extra = 1


class RecipeFavouriteInline(admin.TabularInline):
    model = RecipeFavourite
    extra = 1


class UserFollowingInline(admin.TabularInline):
    model = UserFollowing
    extra = 1
    fk_name = 'following_user'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'num_of_followers',
    )
    list_filter = ('email', 'first_name')
    search_fields = (
        'email',
        'first_name',
    )
    add_fieldsets = ('Extra', {'fields': ('num_of_followers')})
    readonly_fields = ('num_of_followers',)
    list_per_page = 25
    inlines = (
        RecipeFavouriteInline,
        ReciepeShopListInline,
        UserFollowingInline,
    )

    def num_of_followers(self, obj):
        result = obj.followers.all()
        counter = 0
        for _ in result:
            counter += 1
        return counter


admin.site.site_header = 'Foodgram admin panel'
admin.site.site_title = 'Foodgram admin panel'
admin.site.index_title = 'Foodgram models control'
