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
    list_display = ('title', 'author', 'date_posted', 'favorite', 'is_publiction_status')
    list_filter = ('author', 'date_posted')
    filter_horizontal = ('category',)
    autocomplete_fields = ['author']
    search_fields = ('author',)
    ordering = ('title', 'author',)
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
        ('Status publikacji', {
            'fields': ['publiction_status']
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
        'user', 'is_profile_pic', 'is_bio', 'is_phone_number', 'is_newsletter',)
    autocomplete_fields = ['user']
    search_fields = ['user__username']
    ordering = ['user__username']
    filter_horizontal = ('opened_posts',)
    fieldsets = (
        ('Użytkownik', {
            'fields': ['user', 'can_be_author']
        }),
        ('Informacje o użytkowniku', {
            'fields': ('profile_pic', 'bio', 'phone_number', 'gender'),
            'description': 'Informacje dodatkowe na temat użytkownika rozszerzające bazowy model User.',
        }),
        ('Biuletyn i powiadomienia', {
            'fields': ('newsletter', 'miss_news', 'meetups_news', 'opportunities_news')
        }),
        ('Komunikacja od administracji', {
            'fields': ('company_news', 'replay_news', 'development_news')
        }),
        ('Otwarte posty', {
            'fields': ['opened_posts']
        }),
    )


class NewsletterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_added')
    list_filter = ['email']
    search_fields = ['email']
    ordering = ['email']
    readonly_fields = ('date_added',)
    fieldsets = (
        ('Użytkownik', {
            'fields': ['email']
        }),
        ('Data dołączenia do newslettera', {
            'fields': ('date_added',)
        }),
    )


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'status')
    list_filter = ('title', 'date_added')
    search_fields = ('title',)
    ordering = ('title', 'date_added')
    readonly_fields = ('date_added', 'date_modified')
    filter_horizontal = ('email',)
    fieldsets = (
        ('Tytuł', {
            'fields': ['title']
        }),
        ('Treść', {
            'fields': ('text',)
        }),
        ('Status', {
            'fields': ['status_field']
        }),
        ('Użytownicy', {
            'fields': ['email']
        }),
        ('Data utworzenia i ostatniej edycji', {
            'fields': ('date_added', 'date_modified',),
            'classes': ('collapse',)
        }),
    )


class Meetups_newsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'status')
    list_filter = ('title', 'date_added')
    search_fields = ('title',)
    ordering = ('title', 'date_added')
    readonly_fields = ('date_added', 'date_modified')
    fieldsets = (
        ('Tytuł', {
            'fields': ['title']
        }),
        ('Treść', {
            'fields': ('text',)
        }),
        ('Status', {
            'fields': ['status_field']
        }),
        ('Data utworzenia i ostatniej edycji', {
            'fields': ('date_added', 'date_modified',),
            'classes': ('collapse',)
        }),
    )


class AuctionOpportunitiesAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'status')
    list_filter = ('title', 'date_added')
    search_fields = ('title',)
    ordering = ('title', 'date_added')
    readonly_fields = ('date_added', 'date_modified')
    fieldsets = (
        ('Tytuł', {
            'fields': ['title']
        }),
        ('Treść', {
            'fields': ('text',)
        }),
        ('Status', {
            'fields': ['status_field']
        }),
        ('Data utworzenia i ostatniej edycji', {
            'fields': ('date_added', 'date_modified',),
            'classes': ('collapse',)
        }),
    )


class CompanyNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'status')
    list_filter = ('title', 'date_added')
    search_fields = ('title',)
    ordering = ('title', 'date_added')
    readonly_fields = ('date_added', 'date_modified')
    fieldsets = (
        ('Tytuł', {
            'fields': ['title']
        }),
        ('Treść', {
            'fields': ('text',)
        }),
        ('Status', {
            'fields': ['status_field']
        }),
        ('Data utworzenia i ostatniej edycji', {
            'fields': ('date_added', 'date_modified',),
            'classes': ('collapse',)
        }),
    )


class ReplayNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'status')
    list_filter = ('title', 'date_added')
    search_fields = ('title',)
    ordering = ('title', 'date_added')
    readonly_fields = ('date_added', 'date_modified')
    fieldsets = (
        ('Tytuł', {
            'fields': ['title']
        }),
        ('Treść', {
            'fields': ('text',)
        }),
        ('Status', {
            'fields': ['status_field']
        }),
        ('Data utworzenia i ostatniej edycji', {
            'fields': ('date_added', 'date_modified',),
            'classes': ('collapse',)
        }),
    )


class DevelopmentNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'status')
    list_filter = ('title', 'date_added')
    search_fields = ('title',)
    ordering = ('title', 'date_added')
    readonly_fields = ('date_added', 'date_modified')
    fieldsets = (
        ('Tytuł', {
            'fields': ['title']
        }),
        ('Treść', {
            'fields': ('text',)
        }),
        ('Status', {
            'fields': ['status_field']
        }),
        ('Data utworzenia i ostatniej edycji', {
            'fields': ('date_added', 'date_modified',),
            'classes': ('collapse',)
        }),
    )


class ArticleAuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'approved', 'rejected',)
    list_filter = ('email', 'date_added',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number',)
    ordering = ('email', 'date_added',)
    readonly_fields = ('date_added',)
    fieldsets = (
        ('Dane osobowe', {
            'fields': ['first_name', 'last_name', 'email', 'phone_number']
        }),
        ('Aplikacja', {
            'fields': ['experience', 'sample_article']
        }),
        ('Akceptacja regulaminu', {
            'fields': ('accept_terms',)
        }),
        ('Status', {
            'fields': ('approved', 'rejected',)
        }),
        ('Data utworzenia', {
            'fields': ('date_added',),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(NewsletterUser, NewsletterUserAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Meetups_news, Meetups_newsAdmin)
admin.site.register(AuctionOpportunities, AuctionOpportunitiesAdmin)
admin.site.register(CompanyNews, CompanyNewsAdmin)
admin.site.register(ReplayNews, ReplayNewsAdmin)
admin.site.register(DevelopmentNews, DevelopmentNewsAdmin)
admin.site.register(ArticleAuthor, ArticleAuthorAdmin)

admin.site.site_header = 'Administracja Blogu'
admin.site.site_title = 'Administracja Blogu'
