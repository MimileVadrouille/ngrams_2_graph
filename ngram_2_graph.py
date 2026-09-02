#!/usr/bin/env python3
# -*- coding: utf-8 -*

#########################################################################
# This program - Copyright (C) 2026 Antoine de HILLERIN
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#########################################################################


import sys
import os
import optparse
import requests
import matplotlib.pyplot as plt
import json 


# DEBUG option 
verbose=False

######################################################################
def debug_info(message):
  """print a formatted debug message"""
  if verbose :
    print (message)


def getNgrams(query, year_start, year_end, corpus):
  """fetch json data through ngrams API"""
  # hard coded variables
  smoothing=3
  
  # build the json request
  params = {
      "content": query,
      "year_start": year_start,
      "year_end": year_end,
      "corpus": corpus,
      "smoothing": 3
  }

  debug_info ('paramter for ngram : %s' % params)
  
  # header for html request
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36",
  }
  
  # request the json data  and save answer to a json format
  html = requests.get("https://books.google.com/ngrams/json", params=params, headers=headers, timeout=30)
  json_data = html.json() 
  debug_info ('HTML response\n %s' % json_data)
  
  return json_data



def plot_graph (output_json, year_start, year_end, output_file, print_graph, corpora):
  """generate the graph with the json data"""
  year_values = list(range(int(year_start), int(year_end) + 1))
  
  i=1
  plt.figure(figsize=(10,5), dpi=300)
  
  # json data contains several series (words) 
  for series in output_json:
      if corpora is not None:
        string_to_replace=(':%s' % corpora)
        replace_corpora_leg = str(series['ngram']).replace(string_to_replace ,'')
        y_label=str(replace_corpora_leg)
      else:
        y_label=str(series['ngram'])
      # style and color for the different lines of the graph
      if i==1:
          style='-'
          color='black'
      elif i==2:
          style='--'
          color='black'
      elif i==3:
          style=':'
          color='black'
      elif i==4:
          style='-.'
          color='black'
      elif i==5:
          style=(1, (2, 4))
          color='black'
      elif i==6:
          style=(1, (3, 5))
          color='grey'
      else:
          style=(1, (4, 6))
          color='grey'
  
      print ('CURVE %s : %s ' % (i, y_label))
      plt.plot(year_values, series['timeseries'], label=y_label, linestyle=style, color=color, linewidth=1.5)
      i+=1
  
  # graph legend and misc.
  plt.xlabel("Années")
  plt.ylabel("Fréquence")
  
  plt.legend()
  plt.tight_layout()
  
  #plt.title("Google Books Ngram Viewer", pad=10)
  #matplotx.line_labels()  # https://stackoverflow.com/a/70200546/15164646
  
  plt.xticks(list(range(int(year_start), int(year_end) + 2, 20)))
  plt.grid(axis="y", alpha=0.3)
  
  plt.savefig(output_file, dpi=300)
  if print_graph : 
    plt.show()

  return i
  
def check_list (query, nb_curve):
  query_dico=query.split(',')
  nb_words=len(query_dico)+1
  debug_info ('nb words: %s  nb curves: %s' % (nb_words, nb_curve))
  if nb_words != nb_curve: 
    print ("\033[31mWarning le nombre de mot ne correspond pas au nombre de courbes\033[0m")



######################################################################
def parse_options():
  """parse and check command-line options"""
  global verbose

  parser = optparse.OptionParser()
  parser.usage = '%prog [-h][-s start_date][-e end_date][-o output_prefix] -k keyword1,keyword2 \n \
  eg: python ./%prog -k "cathédrale,faubourg,halle"'
  parser.add_option('-k', dest='keywords', metavar=' keyword1,keyword2',
                    help='keywords list separated by comma : keyword1,keyword2')
  parser.add_option('-s', '--start_date', dest='year_start', type=int, metavar='start year', default=1800,
                    help='start date (year) must be an integer')
  parser.add_option('-e', '--end_date', dest='year_end', type=int, metavar='end year', default=2019,
                    help='end date (year) must be an integer')
  parser.add_option('-c', '--corpus', dest='corpus', metavar='corpus', default='fr',
                    help='corpus language : fr , en, en-GB, en-US')
  parser.add_option(      '--corpora', dest='corpora', metavar='corpora', default=None,
                    help='corpora : eng_gb_2019, fre_2019')
  parser.add_option('-o', '--prefix', dest='prefix', metavar='prefix', default=None,
                    help='prefix for graph name')
  parser.add_option('-j', '--json', dest='input_json', metavar='json', default=None,
                    help='json input for graph (no ngram interrogation) ')
  parser.add_option('-p', dest='print_graph', metavar=' ',
                    action='store_true', default=False, help='print and generated graph on the screen')
  parser.add_option('-v', dest='verbose', metavar=' ',
                    action='store_true', default=False, help='Verbose, display more information')
  (options, args) = parser.parse_args()

  verbose = options.verbose

  if options.keywords is None:
    print("Error No keywords")
    parser.print_help()
    sys.exit(1)

  if options.input_json is not None:
    if not os.path.exists(options.input_json):
      print("Error file %s does not exist" % options.input_json)
      sys.exit(1)

  return options


def main():
  """entry point"""
  options = parse_options()

  # save the keyword list and setup file name
  query       = options.keywords
  output_file = query.replace(',', '_')
  output_file = output_file.replace(' ', '-')
  output_file = output_file.replace('\'', '-')

  if options.corpora is not None: 
    new_query=[]
    query_corpora=query.split(',')
    for q in query_corpora:
      new_keyword=('%s:%s' % (q, options.corpora))
      new_query.append(new_keyword)
    debug_info ('Corpora query is %s' % ','.join(new_query))
    query = ('%s' % ','.join(new_query))

  if options.prefix is not None:
    output_file=('%s_%s'% (options.prefix, output_file))
  # options are describe in https://books.google.com/ngrams/info#
  debug_info ('output file   %s' % output_file)
  debug_info ('start year    %s' % options.year_start)
  debug_info ('end year      %s' % options.year_end)
  debug_info ('keywords      %s' % query)
  debug_info ('corpus        %s' % options.corpus)
  debug_info ('corpora       %s' % options.corpora)
  debug_info ('prefix        %s' % options.prefix)
  
  #sys.exit(1)

  # Either use an existing json file or request the json data from ngrams
  if options.input_json is None:
    output_json = getNgrams(query, options.year_start, options.year_end, options.corpus)
    with open(output_file+'.json', 'w', encoding='utf-8') as f:
      json.dump(output_json, f, indent=4, ensure_ascii=False)
    f.close()
  else:
    with open(options.input_json, 'r', encoding='utf-8') as f:
      output_json = json.load(f)
    f.close()

  # finally build the graph
  nb_curve = plot_graph (output_json, options.year_start, options.year_end, output_file, options.print_graph, options.corpora)


  # check if all graph were generated
  check_list (query, nb_curve)



if __name__ == '__main__':
  main()

