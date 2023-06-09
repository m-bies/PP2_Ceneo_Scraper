from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from .models import Product, Review, Advantages, Disadvantages
import re
import csv
from openpyxl import Workbook


def index(request):
    return render(request, 'CeneoScraper/base.html')


def extract(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        url = f'https://www.ceneo.pl/{product_id}#tab=reviews_scroll'
        page = requests.get(url)

        if page.status_code == 200:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            try:
                product_name = soup.find('h1', class_ = 'product-top__product-info__name').text
                product_name = product_name.replace('/', '_')
            except:
                output = 'produkt nie został znaleziony, upewnij się, że product id jest poprawny'
                context = {'output': output}
                return render(request, 'CeneoScraper/extract-results.html', context)

            try:
                product = Product.objects.get(name=product_name)
                output = 'produkt znajduje się już bazie'
                context = {'output': output, 'product_name': product_name}
                return render(request, 'CeneoScraper/extract-results.html', context)

            except:
                product = Product.objects.create(ceneo_id=product_id, name=product_name)
                
            #?tu zbieram opinie
            next_page = True
            while next_page:

                soup = BeautifulSoup(page.text, 'html.parser')
                reviews_tab = soup.select_one('div.js_product-reviews')

                #!z jakiegoś powodu teraz nie dodaje tylko pierwszą stronę z opiniami
                try:
                    all_reviews = reviews_tab.find_all('div', class_='user-post user-post__card js_product-review')
                except:                    
                    context = {'output': 'Produkt nie posiada opinii'}
                    product.delete()
                    return render(request, 'CeneoScraper\extract-results.html', context)

                for single_review in all_reviews:
                    opinion = {}

                    # ?pobieranie dat
                    dates_section = single_review.find('span', class_='user-post__published')
                    dates = dates_section.find_all('time')
                    opinion['data opinii'] = dates[0].attrs['datetime']

                    try:
                        opinion['data zakupu'] = dates[1].attrs['datetime']
                    except Exception as nd:
                        opinion['data zakupu'] = ''

                    # ?pobieranie czy opinia potwierdzona zakupem?
                    try:
                        opinion['wiarygodność'] = single_review.find('div', class_='review-pz').text.strip()
                    except Exception as nd:
                        opinion['wiarygodność'] = 'Opinia nie jest potwierdzona zakupem'

                    # ?pobieranie pozostałych
                    try:
                        opinion['autor'] = single_review.find('span', class_='user-post__author-name').text.strip()
                    except:
                        opinion['autor'] = ''

                    try:
                        opinion['rekomendacja'] = single_review.find('span',
                                                              class_='user-post__author-recomendation').findChild().text.strip()
                    except:
                        opinion['rekomendacja'] = ''

                    try:
                        opinion['ocena produktu'] = single_review.find('span', class_='user-post__score-count').text.strip()
                    except:
                        opinion['ocena produktu'] = ''

                    try:
                        opinion['+1'] = int(single_review.find('span', id=re.compile('votes-yes*')).text.strip())
                    except:
                        pass

                    try:
                        opinion['-1'] = int(single_review.find('span', id=re.compile('votes-no*')).text.strip())
                    except:
                        pass

                    try:
                        opinion['treść'] = single_review.find('div', class_='user-post__text').text.strip()
                    except:
                        opinion['treść'] = ''

                    review_entry = Review.objects.create(product=product, author=opinion['autor'],
                                                       rating=opinion['ocena produktu'],
                                                       purchase_date=opinion['data zakupu'],
                                                       review_date=opinion['data opinii'],
                                                       recommendation=opinion['rekomendacja'],
                                                       confirmed=opinion['wiarygodność'], description=opinion['treść'],
                                                       vote_up=opinion['+1'], vote_down=opinion['-1'])
                    
                    # ?pobieranie zalet i wad
                    try:
                        positives_section = single_review.find('div', class_='review-feature__title review-feature__title--positives').findParent()
                        
                        for item in positives_section.find_all('div', class_='review-feature__item'):
                            advantage = item.text.strip()
                            Advantages.objects.create(review=review_entry, advantage=advantage) 
                    except:
                        pass
                    
                    try:
                        negatives_section = single_review.find('div', class_='review-feature__title review-feature__title--negatives').findParent()

                        for item in negatives_section.find_all('div', class_='review-feature__item'):
                            Disadvantages.objects.create(review=review_entry, disadvantage=item.text.strip())                     
                    except:
                        pass
  
                # ?sprawdzanie czy następna strona istenieje
                try:
                    nextpage = soup.find('a', class_='pagination__item pagination__next').attrs['href']
                    page = requests.get(f'https://ceneo.pl{nextpage}')
                    
                except:
                    next_page = False
                                
            
            context = {'output': 'produkt dodany do bazy'}
            return render(request, 'CeneoScraper/extract-results.html', context)

        else:
            output = 'produkt nie został znaleziony, upewnij się, że product id jest poprawny'
            context = {'output': output}
            return render(request, 'CeneoScraper/extract-results.html', context)
    
    return render(request, 'CeneoScraper\extract.html')




def products(request):

    product_list = Product.objects.all()
    context = {'product_list': product_list}
    return render(request, 'CeneoScraper/product-list.html', context)


def product_page(request, productname):
    product = get_object_or_404(Product, name=productname)
    reviews = Review.objects.filter(product=product)

    #?sortowanie
    sort_by = request.GET.get('sort_by', 'review_date')
    sort_order = request.GET.get('sort_order', 'desc')

    if sort_by == request.GET.get('sort_by'):
        sort_order = 'desc' if sort_order == 'asc' else 'asc'

    if sort_order == 'asc':
        reviews = reviews.order_by(sort_by)
    else:
        reviews = reviews.order_by(f'-{sort_by}')

    #?filtrowanie 
    if 'author' in request.GET:
        reviews = reviews.filter(author__icontains=request.GET['author'])
    if 'rating' in request.GET:
        reviews = reviews.filter(rating__icontains=request.GET['rating'])
    if 'recommendation' in request.GET:
        reviews = reviews.filter(recommendation__icontains=request.GET['recommendation'])
    if 'confirmed' in request.GET:
        reviews = reviews.filter(confirmed__icontains=request.GET['confirmed'])
    if 'purchase_date' in request.GET:
        reviews = reviews.filter(purchase_date__icontains=request.GET['purchase_date'])
    if 'review_date' in request.GET:
        reviews = reviews.filter(review_date__icontains=request.GET['review_date'])
    if 'description' in request.GET:
        reviews = reviews.filter(description__icontains=request.GET['description'])

    context = {'productname': product, 'reviews': reviews, 'sort_by': sort_by, 'sort_order': sort_order,}
    
    return render(request, f'CeneoScraper/product.html', context)

def download(request, productname):
        
        product = Product.objects.get(name = productname)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{productname}.csv"', 

        writer = csv.writer(response)
        writer.writerow(['Author', 
                         'Confirmed', 
                         'Purchase Date', 
                         'Recommendation', 
                         'Rating', 
                         'Review Date', 
                         'Description', 
                         'Vote Up', 
                         'Vote Down', 
                         'Advantages', 
                         'Disadvantages'])

        for review in product.reviews.all():    
            advantages = ', '.join(advantage.advantage for advantage in review.advantages.all())
            disadvantages = ', '.join(disadvantage.disadvantage for disadvantage in review.disadvantages.all())

            writer.writerow([
                review.author,
                review.confirmed,
                review.purchase_date,
                review.recommendation,
                review.rating,
                review.review_date,
                review.description, #.encode(encoding='ascii', errors='ignore')
                review.vote_up,
                review.vote_down,
                advantages,
                disadvantages])

        return response

def download_json(request, productname):
    product = Product.objects.get(name = productname)
    reviews = product.reviews.all()
    data = []

    for review in reviews:
        data.append({
            'author': review.author,
            'confirmed': review.confirmed,
            'purchase_date': review.purchase_date,
            'recommendation': review.recommendation,
            'rating': review.rating,
            'review_date': review.review_date,
            'description': review.description,
            'vote_up': review.vote_up,
            'vote_down': review.vote_down,
            'advantages': [advantage.advantage for advantage in review.advantages.all()],
            'disadvantages': [disadvantage.disadvantage for disadvantage in review.disadvantages.all()]
        })

    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = f'attachment; filename="{productname}.json"'
    return response

def download_xlsx(request, productname):
    product = Product.objects.get(name = productname)
    reviews = product.reviews.all()

    wb = Workbook()
    ws = wb.active
    ws.append(['Author', 'Confirmed', 'Purchase Date', 'Recommendation', 'Rating', 'Review Date', 'Description', 'Vote Up', 'Vote Down', 'Advantages', 'Disadvantages'])

    for review in reviews:
        advantages = ', '.join([a.advantage for a in review.advantages.all()])
        disadvantages = ', '.join([d.disadvantage for d in review.disadvantages.all()])
        ws.append([review.author, 
                   review.confirmed, 
                   review.purchase_date, 
                   review.recommendation, 
                   review.rating, 
                   review.review_date, 
                   review.description, 
                   review.vote_up, 
                   review.vote_down, 
                   advantages,
                   disadvantages])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={productname}.xlsx'

    wb.save(response)

    return response

def charts(request, productname):

    product = Product.objects.get(name = productname)
    reviews = product.reviews.all()

    ratings = []
    recomendations = []

    for review in reviews:
        ratings.append(int(review.rating[0:1]))
        recomendations.append()

    

    

    context = {'productname': productname, 'ratings': ratings}
    return render(request, 'CeneoScraper/charts.html', context)