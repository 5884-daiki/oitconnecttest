from .models import Category,TaggableManager

def related(request):
    context = {
        'category_list': Category.objects.all(),
        'tag_list':TaggableManager.objects.all(),
    }
    return context


