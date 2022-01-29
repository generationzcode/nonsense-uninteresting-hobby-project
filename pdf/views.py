from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from tika import parser
import os
from .models import Document
from .forms import DocumentForm
import json
import pandas as pd
import difflib
import csv

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('view'))
    else:
      for dirpath, dirnames, filenames in os.walk(os.curdir):
        for file in filenames:
          if file.endswith(".csv"):
              os.remove(os.path.join(dirpath, file))
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(request,
        'list.html',
        {'form': form}
    )
def view_products(request):
  #verifies and lets user see
  user=True
  if user == True:
      files = []
      for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".csv")]:
            files.append(os.path.join(dirpath, filename))
      print(files)
      file_names=[]
      for f in files:
        if f.endswith(".csv"):
          file_names.append(f)
      print("sup")
      for v,i in enumerate(file_names):
        print(i)
        report = pd.read_csv(i)
        report_list = report.values.tolist()
        states=["WEST BENGAL"]
        state_cutoffs = [0,1]
        city_names=["BHOPAL", "MUMBAI", "IMPHAL", "SHILLONG", "AIZAWL", "KOHIMA", "BHUBANESWAR", "CHANDIGARH", "JAIPUR", "GANGTOK", "CHENNAI", "HYDERABAD", "AGARTALA", "LUCKNOW", "DEHRADUN", "KOLKATA", "PORT BLAIR", "CHANDIGARH", "DAMAN", "DAMAN", "NEW DELHI", "KAVARATTI", "PUDUCHERRY"]
        state_names = ["ARUNACHAL PRADESH","ANDHRA PRADESH","ASSAM","BIHAR","CHHATTISGARH","GOA","GUJARAT","HARYANA","HIMACHAL PRADESH","JAMMU AND KASHMIR","JHARKHAND","KARNATAKA","KERALA","MADHYA PRADESH","MAHARASHTRA", "MANIPUR","MEGHALAYA","MIZORAM","NAGALAND","ODISHA","PUNJAB","RAJASTHAN","SIKKIM","TAMIL NADU","TELANGANA","TRIPURA","UTTARAKHAND","UTTAR PRADESH","WEST BENGAL","ANDAMAN AND NICOBAR ISLANDS","CHANDIGARH","DADRA AND NAGAR HAVELI","DAMAN AND DIU","DELHI","LAKSHADWEEP","PUDUCHERRY"]
        state_short = ["AP","AR","AS","BR","CT","GA","GJ","HR","HP","JK","JH","KA","KL","MP","MH","MN","ML","MZ","NL","OR","PB","RJ","SK","TN","TG","TR","UT","UP","WB","AN","CH","DN","DD","DL","LD","PY"]
        
        def convert_name(name):
          if not(name.upper() in state_names):
            try:
              return state_names[state_short.index(name.upper())]
            except:
              try:
                return difflib.get_close_matches(name.upper(), state_names)[0]
              except:
                try:
                  return state_names[city_names.index(difflib.get_close_matches(name.upper(),city_names)[0])]
                except:
                  return name.upper()
          return name.upper()
        
        for v,i in enumerate(report_list):
          report_list[v][24] = convert_name(i[24])
        def zerolistmaker(n):
            listofzeros = [0] * n
            return listofzeros
        
        def find_order_index(num):
          for v,i in enumerate(report_list):
            if i[4]==num:
              return v
          return "not there"

        to_delete = []
        
        for v,i in enumerate(report_list):
          if i[3]=="Cancel":
            to_delete.append(report_list[v][4])
          elif i[3]=="Refund":
            original_num=find_order_index(i[4])
            if original_num != "not there":
              if report_list[original_num][9]==i[9]:
                to_delete.append(report_list[v][4])
                to_delete.append(report_list[original_num][4])
              else:
                report_list[original_num][9] = report_list[original_num][9]-i[9]
                report_list[original_num][28]=report_list[original_num][28]+i[28]
                report_list[original_num][27]=report_list[original_num][27]+i[27]
                to_delete.append(report_list[v][4])

        for v,i in enumerate(to_delete):
          for m,n in enumerate(report_list):
            if n[4]==i:
              report_list.pop(m)
              break
        
        for v,i in enumerate(report_list):
          state_name = i[24]
          if state_name.upper() in states:
            state_cutoffs[states.index(state_name.upper())+1] += 1
          else:
            states.append(state_name.upper())
            state_cutoffs.append(1)
        
        for v,i in enumerate(state_cutoffs):
          if v>0:
            state_cutoffs[v] = state_cutoffs[v] + state_cutoffs[v-1]
        for m in states:
          for v,i in enumerate(report_list):
            state_name = i[24]
            if state_name.upper() == m:
              report_list.insert(state_cutoffs[states.index(state_name.upper())], report_list.pop(v))
          
        state_total = zerolistmaker(len(states))
        state_rate_total = zerolistmaker(len(states))
        tax_rates = []
        for i in report_list:
          present_in = False
          for m in tax_rates:
            if (i[30]+i[31]+i[32]+i[33]) == m:
              present_in=True
              break
          if present_in == False:
            tax_rates.append(i[30]+i[31]+i[32]+i[33])
            
        for v,i in enumerate(state_rate_total):
          state_rate_total[v] = zerolistmaker(len(tax_rates))
        
        for i in report_list:
          state_index = states.index(i[24].upper())
          amount = i[28]
          tax_index = tax_rates.index(i[30]+i[31]+i[32]+i[33])
          state_total[state_index] += amount
          state_rate_total[state_index][tax_index] += amount
        columns = report.columns.values.tolist()
        df = pd.DataFrame(report_list, columns = columns)
        length= len(report_list)
        for i in range(length-len(states)):
          states.append("")
          state_total.append("")
          state_rate_total.append(["" for i in range(len(tax_rates))])
        state_rate_total_two=[]
        for i in tax_rates:
          state_rate_total_two.append([])
        for i in state_rate_total:
          for v,m in enumerate(i):
            state_rate_total_two[v].append(m)
        df['states']=states
        df['totals']=state_total
        for v,i in enumerate(tax_rates):
          df[str(i)+"%"] = state_rate_total_two[v]
        arr = df.values.tolist()
        response = HttpResponse(
        content_type='text/csv'
    )
        response['Content-Disposition']='attachment; filename="reportout.csv"'
        writer = csv.writer(response)
        writer.writerow(df.columns.values.tolist())
        for i in arr:
          writer.writerow(i)
        return response

def clear(request):
  for dirpath, dirnames, filenames in os.walk(os.curdir):
    for file in filenames:
        if file.endswith(".pdf"):
            os.remove(os.path.join(dirpath, file))
  return HttpResponse("cleared")