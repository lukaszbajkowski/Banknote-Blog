from django.contrib import admin
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = (
        ('Kategoria', {
            'fields': ['name']
        }),
        ('Opis', {
            'fields': ['description']
        })
    )


class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'is_backgroud', 'favorite')
    list_filter = ('author', 'date_posted')
    filter_horizontal = ('category',)
    autocomplete_fields = ['author']
    search_fields = ('author__username',)
    ordering = ('title', 'author__username',)
    readonly_fields = ('date_posted', 'date_edited')
    fieldsets = (
        ('Autor', {
            'fields': ['author']
        }),
        ('Tytuł', {
            'fields': ['title']
        }),
        ('Treść', {
            'fields': ('content', 'background', 'introduction', 'category'),
        }),
        ('Dodanie do wyróżnionych', {
            'fields': ['favorite']
        }),
        ('Data utworzenia i ostatniej edycji', {
            'fields': ['date_posted', 'date_edited'],
            'classes': ('collapse',)
        }),

    )


class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'date_posted', 'author')
    list_filter = ('author',)
    autocomplete_fields = ['author']
    search_fields = ('author__username',)
    ordering = ('blog', 'author__username',)
    filter_horizontal = ()
    readonly_fields = ('date_posted',)
    fieldsets = (
        ('Autor', {
            'fields': ['author']
        }),
        ('Komentarz', {
            'fields': ['content']
        }),
        ('Wpis', {
            'fields': ['blog']
        }),
        ('Data utworzenia', {
            'fields': ['date_posted', ],
            'classes': ('collapse',)
        }),
    )


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'is_profile_pic', 'is_author_url', 'is_facebook_url', 'is_twitter_url', 'is_instagram_url',
        'is_pinterest_url')
    list_filter = ['user']
    autocomplete_fields = ['user']
    search_fields = ['user__username']
    ordering = ['user__username']
    fieldsets = (
        ('Autor', {
            'fields': ['user']
        }),
        ('Informacje o autorze', {
            'fields': ('bio', 'profile_pic', 'author_url'),
            'description': 'Informacje na temat autora potrzebne do strony o nim.',
        }),
        ('Wizytówka autora', {
            'fields': ('author_quote', 'author_function',),
            'description': 'Informacje na temat autora potrzebne do jego wizytówki.',
        }),
        ('Linki do mediów społecznościowych autora', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'pinterest_url'),
            'description': 'Adresy do mediów społecznościowych autora, nie są wymagane.',
        }),
    )


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'is_profile_pic', 'is_bio', 'is_phone_number')
    # list_filter = ('User__is_profile_pic',)
    autocomplete_fields = ['user']
    search_fields = ['user__username']
    ordering = ['user__username']
    fieldsets = (
        ('Autor', {
            'fields': ['user']
        }),
        ('Informacje o użytkowniku', {
            'fields': ('profile_pic', 'bio', 'phone_number', 'gender'),
            'description': 'Informacje dodatkowe na temat użytkownika rozszerzające bazowy model User.',
        }),
    )


admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)
