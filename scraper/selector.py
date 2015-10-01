
class Selector(object):
    def __init__(self, xpath=None, css=None, callback=None, is_list=False, is_include_child_tags=False, **kwargs):
        self.xpath = xpath
        self.css = css
        self.callback = callback
        self.is_list = is_list
        self.is_include_child_tags = is_include_child_tags

        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_value(self, response):
        if self.xpath:
            return self.__get_xpath_value(response)

        elif self.css:
            return self.__get_css_value(response)

        elif self.callback:
            return self.callback(response)

    def get_value_list(self, response):
        self.is_list = True
        return self.get_value(response)

    def __get_xpath_value(self, response):
        result = response.xpath(self.xpath).extract()
        return self.__process_selector_result(result)

    def __get_css_value(self, response):
        result = response.css(self.css).extract()
        return self.__process_selector_result(result)

    def __process_selector_result(self, result):
        if result and self.is_include_child_tags:
            return '\n'.join(s.strip().replace('\n', '') for s in result).strip()

        if self.is_list:
            return self.__arg_to_iter(result)

        if result:
            return result[0].strip()
        else:
            return None

    def get_element(self, response):
        if self.xpath:
            return self.__get_xpath_element(response)

        elif self.css:
            return self.__get_css_element(response)

        elif self.callback:
            return self.callback(response)

    def get_element_list(self, response):
        self.is_list = True
        return self.get_element(response)

    def __get_xpath_element(self, response):
        result = response.xpath(self.xpath)
        if self.is_list:
            return self.__arg_to_iter(result)
        else:
            return result[0]

    def __get_css_element(self, response):
        result = response.css(self.css)
        if self.is_list:
            return self.__arg_to_iter(result)
        else:
            return result[0]

    @staticmethod
    def get_text(node):
        result = node.xpath("text()").extract()
        if result:
            return result[0].strip()
        else:
            return ""

    @staticmethod
    def get_attribute(node, attr):
        result = node.xpath("@" + attr).extract()
        if result:
            return result[0].strip()
        else:
            return ""

    @staticmethod
    def __arg_to_iter(arg):
        if arg is None:
            return []
        elif hasattr(arg, '__iter__'):
            return arg
        else:
            [arg]