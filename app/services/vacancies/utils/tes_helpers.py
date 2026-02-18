class VacancyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vacancy

    company = Company.objects.create(name="Python Solutions")
    city = City.objects.create(name="Moscow")  
    title = Faker('title')
    platform=Platform.HH
    platform_vacancy_id="id_",
    title=Faker('title'),
    url="https://example.com/vacancy",
    salary="100000 RUB",
    experience="2-3 years",
    employment="Full-time",
    published_at=timezone.now(),
