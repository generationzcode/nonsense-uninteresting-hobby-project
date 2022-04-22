from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import os
from .models import Document
from .forms import DocumentForm
import pandas as pd
import difflib
import csv


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('view'))
    else:
        for dirpath, dirnames, filenames in os.walk(os.curdir):
            for file in filenames:
                if file.endswith(".csv"):
                    os.remove(os.path.join(dirpath, file))
            form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(request, 'list.html', {'form': form})


def list2(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('view_alt'))
    else:
        for dirpath, dirnames, filenames in os.walk(os.curdir):
            for file in filenames:
                if file.endswith(".csv"):
                    os.remove(os.path.join(dirpath, file))
            form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(request, 'list2.html', {'form': form})


def view_products(request):
    #verifies and lets user see
    user = True
    if user == True:
        files = []
        for dirpath, dirnames, filenames in os.walk("."):
            for filename in [f for f in filenames if f.endswith(".csv")]:
                files.append(os.path.join(dirpath, filename))
        print(files)
        file_names = []
        for f in files:
            if f.endswith(".csv"):
                file_names.append(f)
        print("sup")
        for v, i in enumerate(file_names):
            print(i)
            report = pd.read_csv(i)
            report_list = report.values.tolist()
            states = ["WEST BENGAL"]
            state_cutoffs = [0, 1]
            city_names = [
                "BHOPAL", "MUMBAI", "IMPHAL", "SHILLONG", "AIZAWL", "KOHIMA",
                "BHUBANESWAR", "CHANDIGARH", "JAIPUR", "GANGTOK", "CHENNAI",
                "HYDERABAD", "AGARTALA", "LUCKNOW", "DEHRADUN", "KOLKATA",
                "PORT BLAIR", "CHANDIGARH", "DAMAN", "DAMAN", "NEW DELHI",
                "KAVARATTI", "PUDUCHERRY"
            ]
            state_names = [
                "ARUNACHAL PRADESH", "ANDHRA PRADESH", "ASSAM", "BIHAR",
                "CHHATTISGARH", "GOA", "GUJARAT", "HARYANA",
                "HIMACHAL PRADESH", "JAMMU AND KASHMIR", "JHARKHAND",
                "KARNATAKA", "KERALA", "MADHYA PRADESH", "MAHARASHTRA",
                "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "ODISHA",
                "PUNJAB", "RAJASTHAN", "SIKKIM", "TAMIL NADU", "TELANGANA",
                "TRIPURA", "UTTARAKHAND", "UTTAR PRADESH", "WEST BENGAL",
                "ANDAMAN AND NICOBAR ISLANDS", "CHANDIGARH",
                "DADRA AND NAGAR HAVELI", "DAMAN AND DIU", "DELHI",
                "LAKSHADWEEP", "PUDUCHERRY"
            ]
            state_short = [
                "AP", "AR", "AS", "BR", "CT", "GA", "GJ", "HR", "HP", "JK",
                "JH", "KA", "KL", "MP", "MH", "MN", "ML", "MZ", "NL", "OR",
                "PB", "RJ", "SK", "TN", "TG", "TR", "UT", "UP", "WB", "AN",
                "CH", "DN", "DD", "DL", "LD", "PY"
            ]

            def convert_name(name):
                if not (name.upper() in state_names):
                    try:
                        return state_names[state_short.index(name.upper())]
                    except:
                        try:
                            return difflib.get_close_matches(
                                name.upper(), state_names)[0]
                        except:
                            try:
                                return state_names[city_names.index(
                                    difflib.get_close_matches(
                                        name.upper(), city_names)[0])]
                            except:
                                return name.upper()
                return name.upper()

            for v, i in enumerate(report_list):
                report_list[v][24] = convert_name(i[24])

            def zerolistmaker(n):
                listofzeros = [0] * n
                return listofzeros

            def find_order_index(num):
                for v, i in enumerate(report_list):
                    if i[4] == num:
                        return v
                return "not there"

            to_delete = []

            for v, i in enumerate(report_list):
                if i[3] == "Cancel":
                    to_delete.append(report_list[v][4])
                elif i[3] == "Refund":
                    original_num = find_order_index(i[4])
                    if original_num != "not there":
                        if report_list[original_num][9] == i[9]:
                            to_delete.append(report_list[v][4])
                            to_delete.append(report_list[original_num][4])
                        else:
                            report_list[original_num][
                                9] = report_list[original_num][9] - i[9]
                            report_list[original_num][
                                28] = report_list[original_num][28] + i[28]
                            report_list[original_num][
                                27] = report_list[original_num][27] + i[27]
                            to_delete.append(report_list[v][4])

            for v, i in enumerate(to_delete):
                for m, n in enumerate(report_list):
                    if n[4] == i:
                        report_list.pop(m)
                        break

            for v, i in enumerate(report_list):
                state_name = i[24]
                if state_name.upper() in states:
                    state_cutoffs[states.index(state_name.upper()) + 1] += 1
                else:
                    states.append(state_name.upper())
                    state_cutoffs.append(1)

            for v, i in enumerate(state_cutoffs):
                if v > 0:
                    state_cutoffs[v] = state_cutoffs[v] + state_cutoffs[v - 1]
            for m in states:
                for v, i in enumerate(report_list):
                    state_name = i[24]
                    if state_name.upper() == m:
                        report_list.insert(
                            state_cutoffs[states.index(state_name.upper())],
                            report_list.pop(v))

            state_total = zerolistmaker(len(states))
            state_rate_total = zerolistmaker(len(states))
            state_rate_total2 = zerolistmaker(len(states))
            tax_rates = []
            for i in report_list:
                present_in = False
                for m in tax_rates:
                    if (i[30] + i[31] + i[32] + i[33]) == m:
                        present_in = True
                        break
                if present_in == False:
                    tax_rates.append(i[30] + i[31] + i[32] + i[33])

            for v, i in enumerate(state_rate_total):
                state_rate_total[v] = zerolistmaker(len(tax_rates))
                state_rate_total2[v] = zerolistmaker(len(tax_rates))

            for i in report_list:
                state_index = states.index(i[24].upper())
                amount = i[28]
                amount2 = i[29]
                tax_index = tax_rates.index(i[30] + i[31] + i[32] + i[33])
                state_total[state_index] += amount
                state_rate_total[state_index][tax_index] += amount2
                state_rate_total2[state_index][tax_index] += amount
            columns = report.columns.values.tolist()
            df = pd.DataFrame(report_list, columns=columns)
            length = len(report_list)
            for i in range(length - len(states)):
                states.append("")
                state_total.append("")
                state_rate_total.append(["" for i in range(len(tax_rates))])
                state_rate_total2.append(["" for i in range(len(tax_rates))])
            state_rate_total_two = []
            state_rate_total_two2 = []
            for i in tax_rates:
                state_rate_total_two.append([])
                state_rate_total_two2.append([])
            for i in state_rate_total:
                for v, m in enumerate(i):
                    state_rate_total_two[v].append(m)
            for i in state_rate_total2:
                for v, m in enumerate(i):
                    state_rate_total_two2[v].append(m)
            df['states'] = states
            df['totals'] = state_total
            for v, i in enumerate(tax_rates):
                df[str(i) + "%"] = state_rate_total_two[v]
            for v, i in enumerate(tax_rates):
                df[str(i) + "% total"] = state_rate_total_two2[v]
            arr = df.values.tolist()
            response = HttpResponse(content_type='text/csv')
            response[
                'Content-Disposition'] = 'attachment; filename="reportout.csv"'
            writer = csv.writer(response)
            writer.writerow(df.columns.values.tolist())
            for i in arr:
                writer.writerow(i)
            return response


def view_tally(request):
    user = True
    if user == True:
        files = []
        for dirpath, dirnames, filenames in os.walk("."):
            for filename in [f for f in filenames if f.endswith(".csv")]:
                files.append(os.path.join(dirpath, filename))
        print(files)
        file_names = []
        for f in files:
            if f.endswith(".csv"):
                file_names.append(f)
        print("sup")
        for v, i in enumerate(file_names):
            print(i)
            report = pd.read_csv(i)
            report_list = report.values.tolist()
            states = []
            state_cutoffs = [0, 1]

            def word_comp(word1, word2, ind, ind2):
                count = 0
                total = max(len(word1), len(word2))
                for i, v in enumerate(word1):
                    try:
                        if word2[i].lower() == v.lower():
                            count += 1
                    except:
                        break
                    scor_e = count / total
                    if scor_e == 1:
                        if ind == ind2:
                            scor_e = 10
                        else:
                            scor_e = 5
                    return scor_e

            def word_comp_full(word1, name2, ind):
                list_scores = []
                for v, i in enumerate(name2.split(" ")):
                    try:
                        list_scores.append(float(word_comp(word1, i, ind, v)))
                    except:
                        list_scores.append(0)
                print(list_scores)
                return max(list_scores)

            def name_comp(name1, name2):
                score = 0
                name_1 = name1.split(" ")
                if name1 != "" and name2 != "":
                    score += 0.1
                for i, v in enumerate(name_1):
                    score += word_comp_full(v, name2, i)
                #print(score)
                return score

            def top_eval(arr, name1):
                name_1_index = arr.index(name1)
                score_list = []
                for i, v in enumerate(arr):
                    if i == name_1_index:
                        score_list.append(0)
                    else:
                        score_list.append(name_comp(name1, v))
                max_score = max(score_list)

                return arr[score_list.index(max_score)]

            def sorted_it_all():
                sorted_list = []
                target = states[0]
                for i, v in enumerate(states):
                    if i > 0:
                        states[states.index(sorted_list[-1])] = ""
                    sorted_list.append(target)
                    target = top_eval(states, target)
                return sorted_list

            def zerolistmaker(n):
                listofzeros = [0] * n
                return listofzeros

            def find_order_index(num):
                for v, i in enumerate(report_list):
                    if i[4] == num:
                        return v
                return "not there"

            to_delete = []

            for v, i in enumerate(report_list):
                if i[3] == "Cancel":
                    to_delete.append(report_list[v][4])
                elif i[3] == "Refund":
                    original_num = find_order_index(i[4])
                    if original_num != "not there":
                        if report_list[original_num][9] == i[9]:
                            to_delete.append(report_list[v][4])
                            to_delete.append(report_list[original_num][4])
                        else:
                            report_list[original_num][
                                9] = report_list[original_num][9] - i[9]
                            report_list[original_num][
                                28] = report_list[original_num][28] + i[28]
                            report_list[original_num][
                                27] = report_list[original_num][27] + i[27]
                            to_delete.append(report_list[v][4])

            for v, i in enumerate(to_delete):
                for m, n in enumerate(report_list):
                    if n[4] == i:
                        report_list.pop(m)
                        break

            for v, i in enumerate(report_list):
                state_name = str(i[10])
                if state_name.upper() in states:
                    #state_cutoffs[states.index(state_name.upper())+1] += 1
                    pass
                else:
                    states.append(state_name.upper())
                    state_cutoffs.append(1)
            states = sorted_it_all()
            for v, i in enumerate(report_list):
                state_name = str(i[10])
                if state_name.upper() in states:
                    state_cutoffs[states.index(state_name.upper()) + 1] += 1
                else:
                    states.append(state_name.upper())
                    state_cutoffs.append(1)

            for v, i in enumerate(state_cutoffs):
                if v > 0:
                    state_cutoffs[v] = state_cutoffs[v] + state_cutoffs[v - 1]
            for m in states:
                for v, i in enumerate(report_list):
                    state_name = str(i[10])
                    if state_name.upper() == m:
                        report_list.insert(
                            state_cutoffs[states.index(state_name.upper())],
                            report_list.pop(v))

            state_total = zerolistmaker(len(states))
            state_rate_total = zerolistmaker(len(states))
            state_rate_total2 = zerolistmaker(len(states))
            tax_rates = []
            for i in report_list:
                present_in = False
                for m in tax_rates:
                    if (i[30] + i[31] + i[32] + i[33]) == m:
                        present_in = True
                        break
                if present_in == False:
                    tax_rates.append(i[30] + i[31] + i[32] + i[33])

            for v, i in enumerate(state_rate_total):
                state_rate_total[v] = zerolistmaker(len(tax_rates))
                state_rate_total2[v] = zerolistmaker(len(tax_rates))

            for i in report_list:
                state_index = states.index(str(i[10]).upper())
                amount = i[28]
                amount2 = i[29]
                tax_index = tax_rates.index(i[30] + i[31] + i[32] + i[33])
                state_total[state_index] += amount
                state_rate_total[state_index][tax_index] += amount2
                state_rate_total2[state_index][tax_index] += amount
            columns = report.columns.values.tolist()
            df = pd.DataFrame(report_list, columns=columns)
            length = len(report_list)
            for i in range(length - len(states)):
                states.append("")
                state_total.append("")
                state_rate_total.append(["" for i in range(len(tax_rates))])
                state_rate_total2.append(["" for i in range(len(tax_rates))])
            state_rate_total_two = []
            state_rate_total_two2 = []
            for i in tax_rates:
                state_rate_total_two.append([])
                state_rate_total_two2.append([])
            for i in state_rate_total:
                for v, m in enumerate(i):
                    state_rate_total_two[v].append(m)
            for i in state_rate_total2:
                for v, m in enumerate(i):
                    state_rate_total_two2[v].append(m)
            df['states'] = states
            df['totals'] = state_total
            for v, i in enumerate(tax_rates):
                df[str(i) + "%"] = state_rate_total_two[v]
            for v, i in enumerate(tax_rates):
                df[str(i) + "% total"] = state_rate_total_two2[v]
            arr = df.values.tolist()
            response = HttpResponse(content_type='text/csv')
            response[
                'Content-Disposition'] = 'attachment; filename="reportout_2.csv"'
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
