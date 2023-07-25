from fake_useragent import UserAgent
from datetime import datetime
import json

# Scrapy
from bogota_apartments.items import ApartmentsItem
from scrapy.loader import ItemLoader
import scrapy


class HabiSpider(scrapy.Spider):
    name = 'habi'
    allowed_domains = ['habi.co', 'apiv2.habi.co']
    base_url = 'https://apiv2.habi.co/listing-global-api/get_properties'

    def start_requests(self):
        '''
        This function is used to obtain the metrosquare API data by iterating on the operation types and API offsets.
        
        :return: scrapy.Request
        '''
        headers = {
            'X-Api-Key': 'VnXl0bdH2gaVltgd7hJuHPOrMZAlvLa5KGHJsrr6',
            'Referer': 'https://habi.co/',
            'Origin': 'https://habi.co',
            'User-Agent': UserAgent().random
        }

        # hay en total 817 resultados
        for offset in range(0, 832, 32):
            url = f'{self.base_url}?offset={offset}&limit=32&filters=%7B%22cities%22:[%22bogota%22]%7D&country=CO'

            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.body)['messagge']['data']
        self.logger.info(f'Found {len(result)} apartments')

        for item in result:
            property_nid = item['property_nid']
            slug = item['slug']

            headers = {
                'Referer': f'https://habi.co/venta-apartamentos/{property_nid}/{slug}',
                'User-Agent': UserAgent().random
            }

            yield scrapy.Request(
                url=f'https://habi.co/page-data/venta-apartamentos/{property_nid}/{slug}/page-data.json',
                headers=headers,
                callback=self.parse_details
            )

    def parse_details(self, response):
        details = json.loads(response.body)['result']['pageContext']

        loader = ItemLoader(item=ApartmentsItem(), selector=details)
        # TODO: codigo
        loader.add_value('codigo', details['propertyId'])

        details = details['propertyDetail']['property']
        # TODO: tipo propiedad
        loader.add_value('tipo_propiedad', details['detalles_propiedad']['tipo_inmueble'])
        # TODO: tipo operacion
        loader.add_value('tipo_operacion', 'venta')
        # TODO: precio ventas
        loader.add_value('precio_venta', details['detalles_propiedad']['precio_venta'])
        # TODO: area
        loader.add_value('area', details['detalles_propiedad']['area'])
        # TODO: habitaciones
        loader.add_value('habitaciones', details['detalles_propiedad']['num_habitaciones'])
        # TODO: baños
        loader.add_value('banos', details['detalles_propiedad']['baños'])
        # TODO: administracion
        loader.add_value('administracion', details['detalles_propiedad']['last_admin_price'])
        # TODO: parqueaderos
        loader.add_value('parqueaderos', details['detalles_propiedad']['garajes'])
        # TODO: sector
        loader.add_value('sector', details['detalles_propiedad']['zona_mediana'])
        # TODO: estrato 
        loader.add_value('estrato', details['detalles_propiedad']['estrato'])
        # TODO: estado
        # TODO: antiguedad
        loader.add_value('antiguedad', details['detalles_propiedad']['anos_antiguedad'])
        # TODO: latitud
        loader.add_value('latitud', details['detalles_propiedad']['latitud'])
        # TODO: langitud
        loader.add_value('longitud', details['detalles_propiedad']['longitud'])
        # TODO: direccion
        loader.add_value('direccion', details['detalles_propiedad']['direccion'])
        # TODO: featured_interior
        loader.add_value('featured_interior', details['caracteristicas_propiedad'])
        # TODO: featured_exterior
        # TODO: featured_zona_comun
        # TODO: featured_sector
        # TODO: descripcion
        loader.add_value('descripcion', details['descripcion'])
        # TODO: compañia
        # TODO: imagenes
        images = []
        for image in details['images']:
            url = f'https://d3hzflklh28tts.cloudfront.net/{image["url"]}?d=400x400'
            images.append(url)
        loader.add_value('imagenes', images)
        # TODO: website
        loader.add_value('website', 'habi.co')
        # TODO: datetime
        loader.add_value('datetime', datetime.now())

        yield loader.load_item()
        
