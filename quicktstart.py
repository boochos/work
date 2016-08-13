from __future__ import print_function
import httplib2
import os
import warnings
from string import ascii_uppercase

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from woocommerce import API
import json
# from __builtin__ import None

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# sheets
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = '/Users/sebastianweber/Library/Preferences/Autodesk/maya/scripts/client_secret_sheet_sync.json'
APPLICATION_NAME = 'Sheets Sync Credentials'

# woo
wcapi = API(
    url="https://shopinnercircle.ca",
    consumer_key="ck_08e8b06d41059171a59b9e39c4b4f61c4f394280",
    consumer_secret="cs_3eac7c5ca659b59901a63170878e55366934787e",
    wp_api=True,
    version="wc/v1",
    query_string_auth=True,  # Force Basic Authentication as query string true and using under HTTPS
    timeout=10
)


class SyncTools():

    def __init__(self, sheetId='1Hf-HDaj7mjV0gbjpO6Ki9yBrse8W4oI9rh5y3UZlYtU', worksheet='SyncTest'):
        # sheets variables
        self.sheetId = sheetId
        self.worksheet = worksheet
        self.workSheetList = []
        # sheets service
        self.service = self.sheets_get_service()
        # sheets product properties
        self.properties = {}  # {property_name:column_iterator} # use self.columnList to get column name of same int
        self.propertiesClean = {}  # with key names and no values
        self.propertiesPruned = {}  # only compatible keys   woo <--> sheets
        self.propertiesColumn = ''
        self.propertiesRow = ''
        self.columnList = []
        self.skuList = {}  # {sku_number:row_number}
        # populate sheets basic variables
        self.sheets_get_worksheets()
        self.sheets_get_properties()
        # product from sheets
        self.sheetsData = None  # use carefully, be sure to update variables
        # product from woo
        self.wooData = None  # use carefully, be sure to update variables
        self.wooShippingClasses = []
        self.woo_get_ship_classes()

    def sheets_get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def sheets_get_service(self):
        credentials = self.sheets_get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)
        return service

    def sheets_get_read_only(self):
        # properties that dont need updating with this tool as they are managed by other means
        return ['regular_price', 'weight', 'sku']

    def sheets_properties_to_lowercase(self, propertiesList=[]):
        '''
        needs a list
        '''
        # force all keys to lower case, based on how woo names attributes, underscore separator
        for i in range(len(propertiesList) - 1):
            propertiesList[i] = propertiesList[i].lower()
        return propertiesList

    def sheets_get_properties(self):
        '''
        ! assuming 'sku' is in range of a-z column list, if not found, bail
        populates basic variables to look up product info
        '''
        columns = self.build_alphabet_list()
        # my sheet
        if self.worksheet in self.workSheetList:
            for column in columns:
                rangeName = self.worksheet + '!' + column + ':' + column
                # https://developers.google.com/sheets/reference/rest/v4/spreadsheets.values/update
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.sheetId, range=rangeName).execute()
                # print(result)
                values = result['values']
                # print (values, '___here')
                for i in range(len(values)):
                    # print (values[i])
                    if 'sku' in values[i]:
                        print (' --- properties row: ' + str(i + 1) + ' --- of worksheet: \"' + self.worksheet + '\" --- ')
                        self.propertiesRow = str(i + 1)
                        self.propertiesColumn = column
                        rangeName = self.worksheet + '!' + columns[0] + self.propertiesRow + ':' + '$' + self.propertiesRow
                        result = self.service.spreadsheets().values().get(
                            spreadsheetId=self.sheetId, range=rangeName).execute()
                        propertiesList = result['values']
                        propertiesList = propertiesList[0]
                        propertiesList = self.sheets_properties_to_lowercase(propertiesList)
                        # print(values)
                        # build dict with property names and iterator as values, so column names can be created later
                        self.properties = {}
                        for j in range(len(propertiesList)):
                            # print(values[j])
                            try:
                                key = propertiesList[j]
                                self.properties[key] = j
                            except:
                                pass
                        # self.sheets_properties_to_lowercase()
                        self.build_column_list(len(propertiesList) - 1)  # number of columns required to query properties values of product, corresponds to number or properties found
                        # print (self.properties)
                    elif self.propertiesRow:  # sku row found, proceed to find product skus #s
                        if values[i]:  # account for empty fields
                            self.skuList[values[i][0]] = str(i + 1)  # column are 1-based, lists are 0-based, add +1 to iterator for proper row value
                        # build list of skus
                if self.propertiesRow:  # column iteration done, check if sku column found
                    # print(self.skuList)
                    return None  # break loop, sku column encountered
            if not self.propertiesRow:
                print(' --- Properties row not found, SKU field not encountered for worksheet \"' + self.worksheet + '\" --- ')
        else:
            print(' --- Worksheet: ' + self.worksheet + ' doesnt exist in given spreadsheet ID. --- ')

    def sheets_get_property(self, sku='', proprty='weight'):
        # build range string
        row = self.sheets_get_sku_row(sku=sku)
        column = self.columnList[self.properties[proprty]]
        cellRange = column + str(row) + ':' + column + str(row)
        rangeName = self.worksheet + '!' + cellRange
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheetId, range=rangeName, valueRenderOption='UNFORMATTED_VALUE').execute()
        if result:
            if 'values' in result:
                values = result['values'][0][0]
                return values
            else:
                return None

    def sheets_update_property(self, value, sku='', proprty='shipping_class'):
        # build range string
        if proprty in self.properties:
            row = self.sheets_get_sku_row(sku=sku)
            column = self.columnList[self.properties[proprty]]
            cellRange = column + str(row) + ':' + column + str(row)
            rangeName = self.worksheet + '!' + cellRange
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheetId, range=rangeName, body={'values': [[value]]}, valueInputOption='USER_ENTERED').execute()
        else:
            print(' --- Property: ' + proprty + ' doesnt exist in worksheet: ' + self.worksheet)

    def sheets_get_sku_row(self, sku=0):
        rangeName = self.worksheet + '!' + self.propertiesColumn + ':' + self.propertiesColumn
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheetId, range=rangeName).execute()
        values = result['values']
        for i in range(len(values)):
            # print (values[i])
            if sku in values[i]:
                # print (' --- SKU is in row ' + str(i + 1))
                skuRow = str(i + 1)
                return skuRow
        print(values)

    def sheets_get_product(self, sku=0):
        #
        cellRange = self.columnList[0] + self.skuList[sku] + ':' + self.columnList[len(self.columnList) - 1] + self.skuList[sku]
        # build range string
        rangeName = self.worksheet + '!' + cellRange
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheetId, range=rangeName, valueRenderOption='UNFORMATTED_VALUE').execute()
        values = result['values'][0]
        # print(self.properties)
        # pull woo template
        wooData_template = self.woo_get_product(skuSeek=values[self.properties['woo_template']])
        # depending on when self.properties get pulled using them as class wide may cause problems, they may be out of date.
        self.prune_uncompatible_keys(wooData=wooData_template, sheetsData=self.properties)
        # print(values)
        if not values:
            print(' --- No data found. --- ')
        else:
            for key in self.propertiesPruned:
                # print(key, values[self.propertiesPruned[key]])
                try:
                    i = self.propertiesPruned[key]
                    # print(key, i, values[i])
                    # format values to comply with woo format
                    boolType = ['manage_stock', 'in_stock', 'sold_individually', 'featured', 'reviews_allowed']
                    intType = ['stock_quantity', 'parent_id', 'menu_order']
                    listType = ['upsell_ids', 'cross_sell_ids', 'dimensions', 'categories', 'tags', 'images', 'attributes', 'default_attributes', 'variations']
                    strType = ['type', 'status', 'catalog_visibility', 'description', 'short_description', 'sku', 'regular_price', 'sale_price',
                               'date_on_sale_from', 'date_on_sale_to', 'tax_status', 'tax_class', 'backorders', 'weight', 'shipping_class', 'purchase_note']
                    if values[i] != '':  # this if should be under each type, if empty format empty type, ie [], {}, '', 0
                        if key in intType:
                            if not isinstance(values[i], int):
                                # print('int', key)
                                value = eval(values[i])
                            else:
                                value = values[i]
                        elif key in listType:
                            if not isinstance(values[i], list):
                                # check for variations, and reformat appropriately
                                # print('list', key)
                                value = eval(values[i])
                                if key == 'variations':
                                    # need to add query if variations already exist on the product, edit accordingly,
                                    # cant add new ones if editing old ones will do
                                    for k in value:
                                        # print(k)
                                        k['regular_price'] = values[self.propertiesPruned['regular_price']]
                            else:
                                value = values[i]
                        elif key in boolType:
                            if not isinstance(values[i], bool):
                                # print('bool', key)
                                value = eval(values[i])
                            else:
                                value = values[i]
                        else:
                            # print('str', key)
                            value = str(values[i])
                    else:
                        value = ''
                    self.propertiesClean[key] = value
                except:
                    print(' --- get product value exception:  ', key, values[i], type(values[i]))
                    # empty strings tend to error out when posting to woo
                    # sheetD[keyList[i]] = ''
            # remove empty attributes
            self.propertiesClean = self.prune_empty_keys(data=self.propertiesClean)
            # eval string dicts to proper dicts
            # self.propertiesClean = self.string_to_dict(data=self.propertiesClean)
            # print(json.dumps(self.propertiesClean, sort_keys=False, indent=4))
            return self.propertiesClean

    def sheets_update_product(self, skuSeek=''):
        '''
        woo to sheets
        '''
        wooData = self.woo_get_product(skuSeek=skuSeek)
        if wooData:
            row = self.sheets_get_sku_row(sku=wooData['sku'])
            # prune keys, only use keys that exist in both sets of data (from woo and sheets)
            self.prune_uncompatible_keys(wooData=wooData, sheetsData=self.properties, readOnly=True)
            # print(self.properties)
            for key in self.propertiesPruned:
                if key in wooData:
                    # edit sheet
                    value = wooData[key]
                    row = row
                    column = self.columnList[self.propertiesPruned[key]]
                    cellRange = column + str(row) + ':' + column + str(row)
                    # build range string
                    rangeName = self.worksheet + '!' + cellRange
                    # print(cellRange, key, value)
                    if key == 'images':
                        for image in wooData[key]:
                            # remove read-only
                            ro = ['date_created', 'date_modified', ]
                            for r in ro:
                                image.pop(r)
                            # use position 0 as icon
                            if image['position'] == 0:
                                val = "=IMAGE(\"" + image['src'] + "\", 1)"
                                result = self.service.spreadsheets().values().update(
                                    spreadsheetId=self.sheetId, range=self.worksheet + '!' + self.columnList[0] + str(row), body={'values': [[val]]}, valueInputOption='USER_ENTERED').execute()
                                # use as image icon
                        value = ", ".join(str(elm) for elm in wooData[key])
                        if value:
                            value = '[' + value + ']'
                        else:
                            value = ''
                        # print(value)
                        # return None
                    elif key == 'dimensions':
                        value = " ".join(str(elm) for elm in [wooData[key]])
                        # print(value)
                    elif key == 'categories':
                        # will need to properly format the string for woo
                        for category in wooData[key]:
                            # remove read-only, dont track
                            ro = ['count', 'slug', 'parent', 'description', 'display', 'image', 'menu_order']
                            for r in ro:
                                if r in category:
                                    category.pop(r)
                        value = self.sheets_format_stringList(d=wooData[key])
                        # print(value)
                    elif key == 'tags':
                        value = self.sheets_format_stringList(d=wooData[key])
                        # print(value)
                    elif key == 'cross_sell_ids':
                        value = self.sheets_format_stringList(d=wooData[key])
                        # print(value)
                    elif key == 'upsell_ids':
                        value = self.sheets_format_stringList(d=wooData[key])
                        # print(value)
                    elif key == 'default_attributes':
                        value = self.sheets_format_stringList(d=wooData[key])
                        # print(value)
                    elif key == 'attributes':
                        value = self.sheets_format_stringList(d=wooData[key])
                        # print(value)
                    elif key == 'variations':
                        print(json.dumps(wooData[key], sort_keys=True, indent=4))
                        # print(json.dumps(self.properties, sort_keys=True, indent=4))
                        # print(self.columnList)
                        # like images need to strip out read only
                        # currently doesnt work when posting
                        for variation in wooData[key]:
                            # remove read-only
                            # ro = ['id', 'date_created', 'date_modified', 'permalink', 'price', 'on_sale', 'backorders_allowed', 'backordered', 'purchasable', 'shipping_class_id']
                            '''
                            for r in ro:
                                variation.pop(r)
                            '''
                            ro = []
                            keepers = ['attributes', 'sku']
                            for k in variation:
                                if k not in keepers:
                                    ro.append(k)
                            for r in ro:
                                variation.pop(r)
                        # print(json.dumps(value, sort_keys=True, indent=4))
                        value = self.sheets_format_stringList(d=wooData[key])
                    else:
                        # print (type(wooData[key]))
                        p = wooData[key]
                        # isinstance(wooData[key], unicode)
                        if isinstance(wooData[key], unicode):
                            htmls = ['<p>', ',/p>']
                            if htmls[0] in p:
                                value = p.split('<')[1].split('>')[1]
                        elif isinstance(wooData[key], bool):
                            value = wooData[key]
                        elif isinstance(wooData[key], int):
                            value = wooData[key]
                        else:
                            print(' --- none at all, __weird____  --- ', key)
                    # print(cellRange, key, value)
                    result = self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheetId, range=rangeName, body={'values': [[value]]}, valueInputOption='USER_ENTERED').execute()
                    # print(result)
        else:
            print('SKU not found on woo. Nothing to add to sheets.')

    def sheets_update_icon(self, sku=''):
        '''
        woo to sheets
        '''
        wooData = self.woo_get_product(skuSeek=sku)
        if wooData:
            for key in wooData:
                # edit sheet
                if key == 'images':
                    for image in wooData[key]:
                        if image['position'] == 0:
                            val = "=IMAGE(\"" + image['src'] + "\", 1)"
                            print(val)
                            self.sheets_update_property(value=val, sku=sku, proprty='icon')
                            return None

    def sheets_update_icon_bulk(self):
        for sku in self.skuList:
            self.sheets_update_icon(sku)

    def sheets_format_stringList(self, d={}):
        '''
        input should be dict
        reformats to string
        adds square brackets
        '''
        if d:
            value = ", ".join(str(elm) for elm in d)
            if value:
                value = '[' + value + ']'
        else:
            value = ''
        return value

    def sheets_guess_woo_weight_class(self):
        # uses worksheets sku list and builds slug name from weight property per sku
        # hard coded naming structure dependent
        ship_c = 'shipping_class'
        weight = 'weight'
        slug = ''
        for sku in self.skuList:
            val = self.sheets_get_property(sku=sku, proprty=ship_c)
            if not val:
                w = self.sheets_get_property(sku=sku, proprty=weight)
                if w < 0.251:
                    slug = '0-0-250'
                elif w > 0.251 and w < 0.501:
                    slug = '0-251-0-500'
                else:
                    w_rnd = float(str(round(w, 0)))
                    if w > w_rnd:
                        # rounded down, take rounded and add 0.5 for high point, add 001 for low point
                        lo = "%.3f" % (w_rnd + 0.001)
                        hi = "%.3f" % (w_rnd + 0.5)
                        slug = str(lo) + '-' + str(hi)
                        slug = slug.replace('.', '-')
                    else:
                        # rounded up, take rounded and subtract 0.499 for lo point
                        lo = "%.3f" % (w_rnd - 0.499)
                        hi = "%.3f" % (w_rnd)
                        slug = str(lo) + '-' + str(hi)
                        slug = slug.replace('.', '-')
                print(slug)
                if slug in self.wooShippingClasses:
                    self.sheets_update_property(value=slug, sku=sku, proprty=ship_c)
                else:
                    print(' --- Shipping class: ' + slug + ' doesnt exist --- ')

    def sheets_get_worksheets(self):
        # reset sheets list
        self.workSheetList = []
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.sheetId).execute()  # the entire spreadsheet...
        # print(json.dumps(sheet_metadata, sort_keys=True, indent=4))
        sheets = sheet_metadata.get('sheets', '')
        for sh in sheets:
            title = sh.get("properties", {}).get("title")
            self.workSheetList.append(title)
        # print(self.workSheetList)
        # sheet_id = sh.get("properties", {}).get("sheetId", 0)
        # print(sheet_id)
        '''
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheetId, range=rangeName).execute()
        '''

    def woo_get_stuff(self):
        # https://woothemes.github.io/woocommerce-rest-api-docs/?python#create-a-product #docs
        products = wcapi.get("products?per_page=1&category=262,259,258,257").json()  # 262,259,258,257
        for product in products:
            print('--ALL ATTRIBUTES--')
            for key in product:
                print(key, ':', product[key])
                if key == 'id':
                    idee = product[key]
                if key == 'name':
                    newsku = product[key].split(' ')[len(product[key].split(' ')) - 1]
                    # print('%s, %s' % (row[0], row[1]))
            data = {
                "sku": newsku
            }
            if newsku != 'Stand':
                # print(newsku)
                print(wcapi.put("products/" + str(idee), data).json())
        '''
        categories = wcapi.get("products/categories?per_page=40").json()
        cat = []
        for category in categories:
            for key in category:
                if key == 'idee' or key == 'name':
                    cat.append(category[key])
        print(cat)
        '''

    def woo_get_ship_classes(self, ship_c_list=[], page=1):
        # recursive return may only be working cuz list is short enough, may cause problems
        # perhaps list should be part of class variable
        ship_c = wcapi.get("products/shipping_classes?per_page=30&page=" + str(page)).json()
        if ship_c:
            for clas in ship_c:
                for key in clas:
                    if key == 'slug':
                        ship_c_list.append(clas[key])
            self.woo_get_ship_classes(ship_c_list=ship_c_list, page=page + 1)
            # print(json.dumps(ship_c_list, sort_keys=True, indent=4))
            self.wooShippingClasses = ship_c_list
        else:
            return None

    def woo_get_product(self, skuSeek='', page=1):
        # tricky function, all iterations need to carry the return back up the chain
        products = wcapi.get("products?per_page=30&page=" + str(page)).json()
        p = None
        if products:
            # print('seek page: ' + str(page))
            for product in products:
                #p = product
                # print('--ALL ATTRIBUTES--')
                for key in product:
                    # print(key, ':', product[key])
                    if key == 'sku':
                        if product[key] == skuSeek:
                            # print(product)
                            # print(json.dumps(product, sort_keys=True, indent=4))
                            print (' --- woo SKU found: ' + skuSeek + ' --- ')
                            p = product
                    if p:
                        return p
                if p:
                    return p
            if p:
                return p
            p = self.woo_get_product(skuSeek=skuSeek, page=page + 1)
            if p:
                return p
        else:
            print(' --- woo SKU not found: ' + skuSeek + ' --- ')
        return p

    def woo_update_product(self, woo_id='', data={}):
        # print(json.dumps(data, sort_keys=False, indent=4))
        print(wcapi.put("products/" + woo_id, data).json())

    def woo_create_product(self, sku=0):
        # get from sheets
        sheetsData = self.sheets_get_product(sku)
        exists = self.woo_get_product(skuSeek=sku)
        if exists:
            warnings.warn(" --- SKU product number already exists in woo database --- ")
            print(' --- Will update on woo instead --- ')
            self.woo_update_product(woo_id=str(exists['id']), data=sheetsData)
        else:
            print(' --- Creating Product SKU: ' + sku)
            print(wcapi.post("products", sheetsData).json())

    def update_product(self, to='', sku=0):
        '''
        no use for this yet
        '''
        if to == 'sheets':
            self.sheets_update_product()
        elif to == 'woo':
            self.woo_update_product()
        else:
            print('"to", variable not recognized.')

    def woo_bulk_push(self):
        '''
        create or update all skus found in worksheet
        '''
        pass

    def prune_empty_keys(self, data={}):
        removeKeys = []
        # create non matching key list
        for key in data:
            if data[key] == '':
                removeKeys.append(key)
            else:
                pass
                # print('_____not removed____  ', data[key])
        # remove non matching keys
        for key in removeKeys:
            data.pop(key)
        print(' --- empty keys removed --- :  ', removeKeys)
        return data

    def prune_uncompatible_keys(self, wooData={}, sheetsData={}, readOnly=False):
        '''
        prunes uncompatible and resets key value to ''
        '''
        removeKeys = []
        for k in sheetsData:
            self.propertiesPruned[k] = sheetsData[k]
        self.propertiesClean = {}  # build from scratch
        # append read only
        if readOnly:
            for rOnly in self.sheets_get_read_only():
                removeKeys.append(rOnly)
        # create non matching key list
        # print('removed keys___:  ', removeKeys)
        # print('wooData keys___:  ', wooData)
        for key in self.propertiesPruned:
            if key not in wooData:
                # print('Remove this key: ' + key)
                removeKeys.append(key)
            else:
                # reset value to ''
                self.propertiesClean[key] = ''
        # remove non matching keys
        for key in removeKeys:
            if key in self.propertiesPruned:
                self.propertiesPruned.pop(key)
        print(' --- non compatible keys removed --- :  ', removeKeys)

    def build_alphabet_list(self):
        # initial list for column names
        alpha = []
        for a in ascii_uppercase:
            alpha.append(a)
        return alpha

    def build_column_list(self, columnsLength=0):
        alphabet = self.build_alphabet_list()
        i = 0
        j = None
        alphaLength = len(alphabet) - 1
        self.columnList = []
        while len(self.columnList) <= columnsLength:
            column = None
            if j == None:
                self.columnList.append(alphabet[i])
            else:
                # print(j, i)
                column = alphabet[j] + alphabet[i]
                self.columnList.append(column)
            # iterate
            if i < alphaLength:
                i = i + 1
            elif i == alphaLength:
                i = 0
                if j == None:
                    j = 0
                else:
                    j = j + 1
        # print(columnList)

    def string_to_dict(self, data={}):
        for key in data:
            if isinstance(data[key], str):
                if "{" in data[key]:
                    data[key] = eval(data[key])
            else:
                print(data[key], type(data[key]))
        return data


# SANDBOX
sync = SyncTools(worksheet='Legep')
sync.sheets_update_icon_bulk()
# sync.woo_get_ship_classes()
# sync.sheets_guess_woo_weight_class()
# sync.sheets_get_property(sku='test_19I53', proprty='images')
# when uploading to woo, some attributes are dicts, but they should be lists, categories only works if more than 1 is listed,
# if one the value stays as dict, need to force it into a list

# sync.woo_create_product(sku='test_19I53')
# sync.sheets_update_product(skuSeek='test_19I53')
