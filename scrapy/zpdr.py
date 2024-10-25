from re import findall, search
from scrapy.http import Request
from scrapy.spiders import Spider
from artworks.items import ArtworksItem


class TrialSpider(Spider):
    name = "trial"
    start_urls = [
        'http://pstrial-2019-12-16.toscrape.com/browse/insunsh',
        'http://pstrial-2019-12-16.toscrape.com/browse/summertime'
    ]


    def extract_dim(self, dimension, part_amount):
        """
        Extract the numeric values on every occurence of 'cm' (within optional parantheses).
        For multiple parts, we expect the part name to be next to cm
        There could be multiple part dimension content without `\r\n`
            Splitting of the part done from each `cm` index
        """
        rezult = {'height': {}, 'width': {}}
        for part_group in range(part_amount):
            width, height = '', ''
            part_name = ''
            # first occurrence of cm
            # remove cm from the numerical part
            ndx_cm = search('cm', dimension).start()+1
            # remove ` cm*`
            part = dimension[:ndx_cm-1].rstrip()
            # remove everything up to `in.` if any
            ndx_metric_begin = search('in.', part)
            if ndx_metric_begin is None:
                ndx_metric_begin = 0
            else:
                ndx_metric_begin = ndx_metric_begin.end()
            part = part[ndx_metric_begin:].lstrip().lstrip('(').split()
            # extract only width & height as float values
            if len(part) >= 1:
                width = part[0]
            if len(part) >= 3:
                height = part[2]
            # extract part name
            if part_amount > 1:
                remaining_content = dimension[ndx_cm+1:]
                # next sequence of words of the remaining content could be the part name
                # isolate from remaining artefacts
                # remove potential `)` from the end of previous cm
                # remove potential `\r` from end of part name
                part_name = remaining_content\
                    .lstrip(')')\
                    .split('\r')[0]\
                    .lstrip()\
                    .split(' ')[0]
                # extract the remaining dimension on next iteration of the main loop
                dimension=remaining_content
            # for 1 part, name is not provided,
            # use the current iterator number as numeric key
            else:
                part_name = '1'
            # map width (and optional height)
            # depth will be ignored as Item doesn't have such Field
            rezult['width'][part_name] = width
            rezult['height'][part_name] = height
        return rezult
        

    def prop_stringify(self, prop_tup, part_amount):
        if part_amount == 0:
            return ''
        elif part_amount == 1:
            return prop_tup[0][0]
        else:
            prop = ''
            for pair in prop_tup:
                prop += f'{pair[0]} cm {pair[1]}, '
            return prop.rstrip().rstrip(',')
    

    def parse_item(self, response, **kwargs):
        td_dimension ='//div[@id="content"]/table//' \
            + 'td[@class="key" and contains(text(), "Dimensions")]' \
            + '/following-sibling::td/text()'
        dimension = response.xpath(td_dimension).get(default='')
        height, width = '', ''
        part_amount = len(findall('cm',dimension))
        dim_map = None
        if dimension != '' and part_amount > 0:
            # if there is no part, the part element is ''
            dim_map = self.extract_dim(dimension, part_amount)
        if dim_map is not None:
            width = [(width, part) for part, width in dim_map['width'].items()]
            height = [(height, part) for part, height in dim_map['height'].items()]
        artwork = ArtworksItem()
        artwork['url'] = kwargs['url']
        artwork['artist'] = response.css('#body .artist::text').get(default='')
        artwork['title'] = response.xpath('//div[@id="body"]//h1/text()').get()
        artwork['image'] = response.urljoin(response.xpath('//div[@id="body"]/img/@src').get())
        artwork['height'] = self.prop_stringify(height, part_amount)
        artwork['width'] = self.prop_stringify(width, part_amount)
        artwork['description'] = response.css('.description p::text').get(default='')
        artwork['categories'] = kwargs['categories']
        yield artwork


    def parse(self, response):
        # extract data from each artwork article
        to_dig = response.xpath('//div[@id="body"]/div[not(@*)]/a[count(*)>1]/@href').getall()
        # remove query string from category page
        categories = response.url.split('/')[4:]
        paged_cat = categories[-1]
        paged_cat = paged_cat.split('?')[0]
        categories[-1] = paged_cat
        if len(to_dig) > 0:
            for href in to_dig:
                uri = response.urljoin(href)
                prop = {'url': uri, 'categories': categories}
                yield Request(url=uri, callback=self.parse_item, cb_kwargs=prop)
            # go to next page url
            action=response.css('form.next::attr(action)').get()
            param_key=response.css('form.next input[type="hidden"]::attr(name)').get()
            param_val=response.css('form.next input[type="hidden"]::attr(value)').get()
            next_page=response.urljoin(f'{action}?{param_key}={param_val}')
            yield Request(url=next_page,callback=self.parse)
        else:
            # dive into current subcategories
            for uri in response.xpath('//div[@id="subcats"]//div/a/@href').getall():
                if uri is not None:
                    yield response.follow(response.urljoin(uri), callback=self.parse)
