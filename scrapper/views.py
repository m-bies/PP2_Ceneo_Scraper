from django.shortcuts import render, redirect, get_object_or_404
import requests
from bs4 import BeautifulSoup
from .models import Product, Review, Advantages, Disadvantages
import re
from time import sleep


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
            while page:

                soup = BeautifulSoup(page.text, 'html.parser')
                reviews_tab = soup.select_one('div.js_product-reviews')

                try:
                    reviews = reviews_tab.find_all('div', class_='user-post user-post__card js_product-review')
                except AttributeError:
                    context = {'output': 'Produkt nie posiada opinii'}
                    product.delete()
                    return render(request, 'CeneoScraper\extract-results.html', context)

                for review in reviews:
                    opinion = {}

                    # ?pobieranie dat
                    dates_section = review.find('span', class_='user-post__published')
                    dates = dates_section.find_all('time')
                    opinion['data opinii'] = dates[0].attrs['datetime']

                    try:
                        opinion['data zakupu'] = dates[1].attrs['datetime']
                    except Exception as nd:
                        opinion['data zakupu'] = ''

                    # ?pobieranie czy opinia potwierdzona zakupem?
                    try:
                        opinion['wiarygodność'] = review.find('div', class_='review-pz').text.strip()
                    except Exception as nd:
                        opinion['wiarygodność'] = 'Opinia nie jest potwierdzona zakupem'

                    # ?pobieranie pozostałych
                    try:
                        opinion['autor'] = review.find('span', class_='user-post__author-name').text.strip()
                    except:
                        opinion['autor'] = ''

                    try:
                        opinion['rekomendacja'] = review.find('span',
                                                              class_='user-post__author-recomendation').findChild().text.strip()
                    except:
                        opinion['rekomendacja'] = ''

                    try:
                        opinion['ocena produktu'] = review.find('span', class_='user-post__score-count').text.strip()
                    except:
                        opinion['ocena produktu'] = ''

                    try:
                        opinion['+1'] = int(review.find('span', id=re.compile('votes-yes*')).text.strip())
                    except:
                        pass

                    try:
                        opinion['-1'] = int(review.find('span', id=re.compile('votes-no*')).text.strip())
                    except:
                        pass

                    try:
                        opinion['treść'] = review.find('div', class_='user-post__text').text.strip()
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
                        positives_section = review.find('div', class_='review-feature__title--positives').findParent()
                        
                        for item in positives_section.find_all('div', class_='review-feature__item'):
                            advantage = item.text.strip()
                            Advantages.objects.create(review=review_entry, advantage=advantage) 
                    except:
                        pass
                    
                    try:
                        negatives_section = review.find('div', class_='review-feature__title review-feature__title--negatives').findParent()

                        for item in negatives_section.find_all('div', class_='review-feature__item'):
                            Disadvantages.objects.create(review=review_entry, disadvantage=item.text.strip())                     
                    except:
                        pass

                    
                    
                # ?sprawdzanie czy następna strona istenieje
                try:
                    nextpage = soup.find('a', class_='pagination__item pagination__next').attrs['href']
                except:
                    ValueError
                    nextpage = None

                # ?wygenerowanie kolejnej strony
                if nextpage != None:
                    page = requests.get(f'https://ceneo.pl{nextpage}')
                else:
                    break
            
            
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
