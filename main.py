# -*- coding: utf-8 -*-
import sys
import json
import base64
import re
import urllib
import urllib2
import time
import xbmc
import xbmcaddon
import xbmcplugin
import unicodedata 
from string import maketrans 

API_KEY = "57983e31fb435df4df77afb854740ea9"
BASE_URL = "http://api.themoviedb.org/3"
pag_esp = u'%20%28castellano%20OR%20espa%C3%B1ol%20OR%20esp%20OR%20spanish%20OR%20newpct%20OR%20elitetorrent%29'
pag_ita = u"%20%2B%28ITA%20OR%20italian%29"
pag_rus = "%20%2B%28rus%29"
pag_fra = "%20%2B%28french%29"
no_ITA = "%20-ITA"
screener = "%20-screener%20-CAM%20-Cam%20-camrip%20-TeleSync%20-TS%20%-camlat"
sin_3d = "%20-3D"

alta_definicion = "+%28720p%20OR%201080p%20OR%20720%20OR%201080%20OR%20microhd%29"

__addon__ = xbmcaddon.Addon(id="script.pulsar.kiasmulti")
__proxy__ = __addon__.getSetting("url_proxy")
__idioma__ = __addon__.getSetting("idioma_xml")
use_screener = __addon__.getSetting("use_screener")
use_3D = __addon__.getSetting("use_3D")
only_HD = __addon__.getSetting("only_HD")
IDIOMA = __idioma__
HEADERS = {
    "Referer": BASE_URL,
}
PAYLOAD = json.loads(base64.b64decode(sys.argv[1]))

def search(query):
    busqueda_completa = __proxy__ + "search?q=%s" % urllib.quote_plus(query)
    response = urllib2.urlopen(busqueda_completa)
    data = response.read()
    if response.headers.get("Content-Encoding", "") == "gzip":
        import zlib
        data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
    return [{"uri": magnet} for magnet in re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)]

def search_episode(imdb_id, tvdb_id, name, season, episode):
    url_pelicula = "http://api.themoviedb.org/3/find/%s?api_key=57983e31fb435df4df77afb854740ea9&language=%s&external_source=imdb_id" % (imdb_id, IDIOMA)
    pelicula = urllib2.urlopen(url_pelicula)
    texto1 = json.loads(pelicula.read())
    texto2 = texto1['tv_results']
    texto3 = texto2[0]

    nombre = texto3.get("name")
    if nombre == "24" and season == 9 and IDIOMA == 'es':
                 nombre = u"24 vive otro dia"
                 name = u"24 live other day"
                 season = 1
 #   nombre = nombre.replace(":", " ")
 #   nombre = nombre.replace(" ", "%20")
    nombre = nombre.replace(u'á', "a")
    nombre = nombre.replace(u'é', "e")
    nombre = nombre.replace(u'í', "i")
    nombre = nombre.replace(u'ó', "o")
    nombre = nombre.replace(u'ú', "u")  
    
    temporada = "" 
    pag_bus = ""
    suf_idioma = ""
    if IDIOMA == 'es':
            suf_idioma = pag_esp
    elif IDIOMA == 'it':
            suf_idioma = pag_ita
    elif IDIOMA == 'ru':
            suf_idioma = pag_rus 
    elif IDIOMA == 'fr':
            suf_idioma = pag_fra 
    
    if nombre.lower() <> name.lower():
        nombre2 = '%22' + name + '%22' + suf_idioma
        nombre = '%28%22' + nombre + '%22%20OR%20' + nombre2 + '%29' 
   
    else:    
        nombre = '%22' + name + '%22' + suf_idioma   
    nombre = nombre.replace(":", " ")     
    nombre = nombre.replace(' ', '%20')
    capitulo = "%s%dX%02d%s%d%02d%s" % ("%20%28",season, episode, "%20OR%20", season, episode, "%20%29")
    busqueda_completa = __proxy__ + "usearch/" + nombre + capitulo + "/"

    xbmc.log('Victor: %s' % busqueda_completa.encode('utf-8'), xbmc.LOGDEBUG)
    datos_encontrados = "1"
    try:
       response = urllib2.urlopen(busqueda_completa.encode('utf-8')) 
    except urllib2.HTTPError as e:
 #     if e.code = '404':        
             busqueda_completa = __proxy__ + "usearch/" + name + capitulo
             if IDIOMA == 'es':
               
               
               
                busqueda_completa = busqueda_completa + no_ITA
             try:
                response = urllib2.urlopen(busqueda_completa.encode('utf-8')) 
             except urllib2.HTTPError as e:
                xbmc.log('Victor: no encuentra nada %s ' %e.code , xbmc.LOGDEBUG)
                datos_encontrados = "0"
 #     if e.code = '404':
    if datos_encontrados == "0":
        data = "" 
    else: 
        data = response.read()
        xbmc.log('Victor: busqueda completa' , xbmc.LOGDEBUG)

        if response.headers.get("Content-Encoding", "") == "gzip":
          import zlib
          data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
    retorno_datos = [{"uri": magnet} for magnet in re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)]
        
    return retorno_datos           
 #   return search("%s S%02dE%02d" % (name, season, episode))

def elimina_tildes(s): 
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')) 

def search_movie(imdb_id, name, year):
  
  # Busqueda de titulo en idioma de audio ------------------------ 
    if IDIOMA <> 'en':
      inicio_proceso = time.time()
      url_pelicula = "http://api.themoviedb.org/3/find/%s?api_key=57983e31fb435df4df77afb854740ea9&language=%s&external_source=imdb_id" % (imdb_id, IDIOMA)

      pelicula = urllib2.urlopen(url_pelicula)
      texto1 = json.loads(pelicula.read())
      fin_proceso = time.time()
      tiempo_total = fin_proceso - inicio_proceso
      xbmc.log(' Victor Tiempo busqueda nombre espanol: %s' % tiempo_total, xbmc.LOGDEBUG)

      
      texto2 = texto1['movie_results']
      texto3 = texto2[0]
      nombre = texto3.get("title")
      nombre = nombre.replace(u'á', "a")
      nombre = nombre.replace(u'é', "e")
      nombre = nombre.replace(u'í', "i")
      nombre = nombre.replace(u'ó', "o")
      nombre = nombre.replace(u'ú', "u")
    else:
      nombre = name  
  # -------------------------------------------------------------
    var_1 = "%s" % name
    var_2 = "%s" % nombre
    suf_idioma = ""
 
      
    if IDIOMA == 'es':
            suf_idioma = pag_esp
    elif IDIOMA == 'it':
            suf_idioma = pag_ita
    elif IDIOMA == 'ru':
            suf_idioma = pag_rus 
    elif IDIOMA == 'fr':
            suf_idioma = pag_fra         
    nombre2 = '%22' + name + '%22' + suf_idioma 
    if var_1 == var_2:
        nombre = nombre2
    else:    
        nombre = '%22' + nombre + '%22' 
  #----Calidad ------------------------------------      
    if only_HD == "true": 
             nombre = nombre + alta_definicion 
    else: 
        if use_screener == "true": 
          nombre = nombre + screener
          
    if use_3D == "true": 
         xbmc.log(' Victor Con 3D', xbmc.LOGDEBUG)   
    else:     
         nombre = nombre + sin_3d    
  #----------------------------------------------------------       
    nombre = nombre.replace(":", " ")
    nombre = nombre.replace(" ", "%20")   
    
    
    busqueda_completa = __proxy__ + "usearch/" + nombre + u"%20category:movies/"
    xbmc.log('Victor: %s' % busqueda_completa.encode('utf-8'), xbmc.LOGDEBUG)
    datos_encontrados = "1"
    try:
       response = urllib2.urlopen(busqueda_completa.encode('utf-8')) 
    except urllib2.HTTPError as e:
 #     if e.code = '404':
             xbmc.log('Victor: no encuentra nada %s ' %e.code , xbmc.LOGDEBUG)
             datos_encontrados = "0" 

    if datos_encontrados == "0":
        data = "" 
    else: 
        data = response.read()
        xbmc.log('Victor: busqueda completa' , xbmc.LOGDEBUG)

        if response.headers.get("Content-Encoding", "") == "gzip":
          import zlib
          data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
    retorno_datos = [{"uri": magnet} for magnet in re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)]
        
    return retorno_datos

urllib2.urlopen(
    PAYLOAD["callback_url"],
    data=json.dumps(globals()[PAYLOAD["method"]](*PAYLOAD["args"]))
)

