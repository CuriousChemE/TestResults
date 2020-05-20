from bokeh.io import output_file, show, curdoc
from bokeh.models import ColumnDataSource, FactorRange, Slider, NumeralTickFormatter, Div, LabelSet
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.layouts import column, row, grid
from bokeh.models.widgets import DataTable, TableColumn

# output_file("test_interp.html")
palette = ["#718dbf", "#e84d60"]

labels=['Random Testing', 'Symptomatic?', 'Symptomatic and Tested', 'Asymptomatic and Tested']
sublabels=['Positive','Negative']

LabelT1=['COVID-19 AND Positive Test Result','NO COVID-19 BUT Positive Test Result', 'COVID-19 AND Negative Test Result','NO COVID-19 AND Negative Test Result']
LabelT2=['Have COVID-19 AND Symptomatic','Do NOT Have COVID-19 BUT Symptomatic', 'Have COVID-19 BUT Asymptomatic','Do NOT Have COVID-19 AND Asymptomatic']
LabelT3=['COVID-19 AND Positive Test Result','NO COVID-19 BUT Positive Test Result', 'COVID-19 AND Negative Test Result','NO COVID-19 AND Negative Test Result']
LabelT4=['COVID-19 AND Positive Test Result','NO COVID-19 BUT Positive Test Result', 'COVID-19 AND Negative Test Result','NO COVID-19 AND Negative Test Result']

# initial parameter values
params=0.02,0.3,0.03,0.5,0.005
pv = 0.02
fn = 0.3
fp = 0.03
ac = 0.5
sn = 0.005

# generate results
# Bayes rule invoked multiple times, define as function
def BayesRule(P1,P2,P3):
    # params all in fractions
    Updated=(P1*P2)/((P1*P2)+P3*(1-P1))
    Pop=1000
    PlusPlus=Pop*P1*P2
    PlusMinus=Pop*P3*(1-P1)
    MinusPlus=Pop*P1*(1-P2)
    MinusMinus=(1000-(PlusPlus+PlusMinus))-MinusPlus
    UpdatedNegative=MinusPlus/(MinusPlus+MinusMinus)
    return Updated,UpdatedNegative,round(PlusPlus),round(PlusMinus),round(MinusPlus),round(MinusMinus)

# will re-run this function each time user updates a parameter
def covid_testing(Prevalence,FalseNeg,FalsePos,Asymptomatic,PrevSymptNoCovid):
    # params all in %
    # Prevalence,FalseNeg,FalsePos,Asymptomatic,PrevSymptNoCovid=parameters
    # random testing
    TrueNeg=1-FalseNeg
    NotAsympt=1-Asymptomatic
    LikelihoodPosTest=BayesRule(Prevalence,TrueNeg,FalsePos)
    LikelihoodSymptoms=BayesRule(Prevalence,NotAsympt,PrevSymptNoCovid)
    LikelihoodPosSymptoms=BayesRule(LikelihoodSymptoms[0],TrueNeg,FalsePos)
    LikeAsympt=LikelihoodSymptoms[4]/(LikelihoodSymptoms[4]+LikelihoodSymptoms[5])
    LikelihoodPosAsympt=BayesRule(LikeAsympt,TrueNeg,FalsePos)
    ptest=LikelihoodPosTest[0],LikelihoodSymptoms[0],LikelihoodPosSymptoms[0],LikelihoodPosAsympt[0]
    ntest=LikelihoodPosTest[1],LikelihoodSymptoms[1],LikelihoodPosSymptoms[1],LikelihoodPosAsympt[1]
    # also return confusion matrix for each case
    TableRandom=LikelihoodPosTest[2],LikelihoodPosTest[3],LikelihoodPosTest[4],LikelihoodPosTest[5]
    TableSymptom=LikelihoodSymptoms[2],LikelihoodSymptoms[3],LikelihoodSymptoms[4],LikelihoodSymptoms[5]
    TablePosSympt=LikelihoodPosSymptoms[2],LikelihoodPosSymptoms[3],LikelihoodPosSymptoms[4],LikelihoodPosSymptoms[5]
    TablePosAsympt=LikelihoodPosAsympt[2],LikelihoodPosAsympt[3],LikelihoodPosAsympt[4],LikelihoodPosAsympt[5]
    data = {'labels' : labels,
        'Positive'   : ptest,
        'Negative'   : ntest}
    T1={'labels': LabelT1,
       'Values': TableRandom}
    T2={'labels': LabelT2,
       'Values': TableSymptom}
    T3={'labels': LabelT3,
       'Values': TablePosSympt}
    T4={'labels': LabelT4,
       'Values': TablePosAsympt}
    # return LikelihoodPosTest, LikelihoodSymptoms,LikelihoodPosSymptoms,LikelihoodPosAsympt
    return data,T1,T2,T3,T4

Outcomes,t1,t2,t3,t4=covid_testing(pv,fn,fp,ac,sn)
# set up the data tables (number of each category for each case)
S1=ColumnDataSource(t1)
S1columns = [
        TableColumn(field="labels",title="People Tested at Random", width=250),
        TableColumn(field="Values",title="1000", width=50),
    ]
data_table1 = DataTable(source=S1, columns=S1columns, width=300, height=280, index_position=None)
S2=ColumnDataSource(t2)
S2columns = [
        TableColumn(field="labels",title="People in General Population", width=250),
        TableColumn(field="Values",title="1000", width=50),
    ]
data_table2 = DataTable(source=S2, columns=S2columns, width=300, height=280, index_position=None)

S3=ColumnDataSource(t3)
S3columns = [
        TableColumn(field="labels",title="Symptomatic People Tested", width=250),
        TableColumn(field="Values",title="1000", width=50),
    ]
data_table3 = DataTable(source=S3, columns=S3columns, width=300, height=280, index_position=None)
S4=ColumnDataSource(t4)
S4columns = [
        TableColumn(field="labels",title="Asymptomatic People Tested", width=250),
        TableColumn(field="Values",title="1000", width=50),
    ]
data_table4 = DataTable(source=S4, columns=S4columns, width=300, height=280, index_position=None)

# set up bar chart
x = [ (label, sublabel) for label in labels for sublabel in sublabels ]
counts = sum(zip(Outcomes['Positive'], Outcomes['Negative']), ()) # like an hstack

source = ColumnDataSource(data=dict(x=x, counts=counts))
# TOOLTIPS=[('prob','@counts')]
# barlabels = LabelSet(x='x', y=('counts'*100), text='counts', level='glyph',
        # x_offset=-13.5, y_offset=0, source=source, render_mode='canvas')

p = figure(x_range=FactorRange(*x), y_range=[0,1], plot_height=450, title="Test Result Interpretation",
           toolbar_location=None, tools="")

p.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",
       fill_color=factor_cmap('x', palette=palette, factors=sublabels, start=1, end=2))

# p.add_layout(barlabels)

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None
p.yaxis.axis_label = 'Likelihood of Having Covid-19'
p.yaxis.formatter = NumeralTickFormatter(format='0 %')

# Set up widgets

Prevalence = Slider(title="Prevalence COVID-19 in Population %", value=2, start=0, end=100, step=1)
FalseNeg = Slider(title="Sensitivity, %", value=70, start=0, end=100, step=1)
FalsePos = Slider(title="Specificity, %", value=97, start=0, end=100, step=1)
AsymptCase = Slider(title="Asymptomatic Cases, %", value=50, start=0, end=100, step=1)
SymptNoCovid = Slider(title="Likelihood of Symptoms without COVID-19, %", value=0.5, start=0, end=10, step=0.5)


#set up callback
def update_data(attrname, old, new):

    # Get the current slider values
    pv = .01*Prevalence.value
    fn = .01*(100-FalseNeg.value)
    fp = .01*(100-FalsePos.value)
    ac = .01*AsymptCase.value
    sn = .01*SymptNoCovid.value

    # Generate the new results
    UpdatedResults,tt1,tt2,tt3,tt4 = covid_testing(pv,fn,fp,ac,sn)
    counts = sum(zip(UpdatedResults['Positive'], UpdatedResults['Negative']), ()) # like an hstack
    labs=['Random Testing', 'Symptomatic?', 'Symptomatic and Tested', 'Asymptomatic and Tested']
    subs=['Positive','Negative']
    x = [ (label, sublabel) for label in labs for sublabel in subs ]
    # source = ColumnDataSource(data=dict(x=x, counts=counts))
    # added .update
    source.data=dict(x=x,counts=counts)
    # pal = ["#718dbf", "#e84d60"]
    # p.vbar(x='x', top='counts', source=source, line_color="white", 
    #       fill_color=factor_cmap('x', palette=pal, factors=subs, start=1, end=2))

    # source.data = dict(x=x, y=y)
    S1.data=dict(labels=LabelT1,Values=tt1['Values'])
    S2.data=dict(labels=LabelT2,Values=tt2['Values'])
    S3.data=dict(labels=LabelT3,Values=tt3['Values'])
    S4.data=dict(labels=LabelT4,Values=tt4['Values'])
    # global data_table1
    # data_table1.update()

for w in [Prevalence, FalseNeg, FalsePos, AsymptCase, SymptNoCovid]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(Prevalence, FalseNeg, FalsePos, AsymptCase, SymptNoCovid)

# read in html strings for header and footer
with open ("BayesHeader.txt", "r") as myfile:
    texttop=myfile.read()
with open ("BayesFooter.txt", "r") as myfile:
    textbottom=myfile.read()

divtop = Div(text=texttop, sizing_mode="scale_width")   
divbottom = Div(text=textbottom, sizing_mode="scale_width")


# create the document
curdoc().add_root(divtop)
curdoc().add_root(row(inputs, p, width=800))
curdoc().add_root(row(data_table1,data_table2,data_table3,data_table4))
curdoc().add_root(divbottom)
curdoc().title = "CovTables"
# show(data_table)
