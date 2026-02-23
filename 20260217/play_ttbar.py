# need to download file MERGED/ntuples-mc/TTJets_TuneZ2_7TeV-madgraph-tauola/010003/ttbarSel_merged.root
# via this link: https://cernbox.cern.ch/s/UmbXF1XxVrT4whQ
# or download it from git https://github.com/zenaiev/hep2026_codes/20260127/ttbarSel_merged.root

import ROOT
import array
#import time
from time import sleep

nrepeat = 1
#nrepeat = 1000
fname = 'ttbarSel_merged.root' # 7980 events, signal ttbar MC
#f = ROOT.TFile(fname)
#f.ls()
#t = f.Get('tree')
t = ROOT.TChain('tree')
for i in range(nrepeat):
  t.Add(fname)
#t.Print()

# imperative style using loop over TTree and TTree::GetEntry()
# nrepeat = 10000: 324 sec (without SetBranchStatus() 760 sec)
if 0:
  t.SetBranchStatus('*', 0)
  mcNu = array.array('f', [0.]*4)
  t.SetBranchStatus('mcLp', 1)
  t.SetBranchAddress('mcLp', mcNu)
  mcTbar = array.array('f', [0.]*4)
  t.SetBranchStatus('mcLm', 1)
  t.SetBranchAddress('mcLm', mcTbar)
  selected = 0
  for i in range(t.GetEntries()):
    #t.mcLp # accessing TTree data this way is VERY SLOW
    t.GetEntry(i)
    if ROOT.TMath.Sqrt(mcNu[0]**2+mcNu[1]**2)>20. and ROOT.TMath.Sqrt(mcTbar[0]**2+mcTbar[1]**2)>20.:
      selected += 1
  print(f'{selected} / {t.GetEntries()} = {selected / t.GetEntries():.2f}')

# declarative style using TTree methods (TTree::Draw() etc.)
# nrepeat = 10000: 43 sec
if 0:
  t.Draw('mcT[0]>>h(20,-100.,100.)','sqrt(mcLp[0]**2+mcLp[1]**2)>20. && sqrt(mcLm[0]**2+mcLm[1]**2)>20.','goff')
  h = ROOT.gDirectory.Get('h')
  print(f'{h.GetEntries()} / {t.GetEntries()} = {h.GetEntries() / t.GetEntries():.2f}')

# declarative style using RDataFrame
# nrepeat = 10000: 12 sec, without EnableImplicitMT() 43 sec
if 0:
  ROOT.EnableImplicitMT() # parallel
  rdf = ROOT.RDataFrame('tree', [fname]*nrepeat)
  rdf = rdf.Define('mcLp_pt', 'sqrt(pow(mcLp[0],2.)+pow(mcLp[1],2.))')
  rdf = rdf.Define('mcLm_pt', 'sqrt(pow(mcLm[0],2.)+pow(mcLm[1],2.))')
  rdf_selected = rdf.Filter('mcLp_pt>20 && mcLm_pt>20')
  nevents = rdf.Count()
  selected = rdf_selected.Count()
  print(f'{selected.GetValue()} / {nevents.GetValue()} = {selected.GetValue() / nevents.GetValue():.2f}')
  print(f'number of runs: rdf = {rdf.GetNRuns()}, rdf_selected = {rdf_selected.GetNRuns()}') # should be 1

if 0:
  # increase font size
  font=42
  tsize=0.04
  ROOT.gStyle.SetTextFont(font)
  ROOT.gStyle.SetTitleSize(tsize, "x")
  ROOT.gStyle.SetTitleSize(tsize, "y")
  ROOT.gStyle.SetLabelSize(tsize, "x")
  ROOT.gStyle.SetLabelSize(tsize, "y")
  # disable histogram title
  ROOT.gStyle.SetOptTitle(0)
  c = ROOT.TCanvas('c', '', 1600, 800)
  c.Divide(2, 2)
  c.cd(1)
  t.Draw('mcT[0]>>h0(100, -500., 500.)')
  c.cd(2)
  t.Draw('mcT[1]>>h1(100, -500., 500.)')
  c.cd(3)
  t.Draw('mcT[2]>>h2(100, -500., 500.)')
  c.cd(4)
  t.Draw('mcT[3]>>h3(100, -500., 500.)')
  h3 = ROOT.gDirectory.Get('h3')
  h3.GetXaxis().SetTitle('m [GeV]')
  h3.GetYaxis().SetTitle('Events / #sqrt{10^{2}} #it{GeV}')
  c.SaveAs('c.pdf')

if 0:
  # calculate correlation between px(t)[x] and px(tbar)[y]
  # part1 + part2 = top + antitop [LO] + q,g,... [proton remnant + radiation beyond LO]
  # px(part1) = px(part2) = 0 [at LO]
  # px(top) + px(antitop) = px(part1) = px(part2) = 0 [at LO]
  # py(top) + py(antitop) = py(part1) = py(part2) = 0 [at LO]
  t.SetBranchStatus('*', 0)
  mcNu = array.array('f', [0.]*4)
  t.SetBranchStatus('mcT', 1)
  t.SetBranchAddress('mcT', mcNu)
  mcTbar = array.array('f', [0.]*4)
  t.SetBranchStatus('mcTbar', 1)
  t.SetBranchAddress('mcTbar', mcTbar)
  mean_x = 0
  mean_y = 0
  mean_xx = 0
  mean_yy = 0
  mean_xy = 0
  n = t.GetEntries()
  g_px = ROOT.TGraph()
  for i in range(n):
    t.GetEntry(i)
    mean_x += mcNu[0]
    mean_y += mcTbar[0]
    mean_xx += mcNu[0]**2
    mean_yy += mcTbar[0]**2
    mean_xy += mcNu[0]*mcTbar[0]
    g_px.AddPoint(mcNu[0],mcTbar[0])
  mean_x /= n
  mean_y /= n
  mean_xx /= n
  mean_yy /= n
  mean_xy /= n
  sigma_x = (mean_xx - mean_x**2)**0.5
  sigma_y = (mean_yy - mean_y**2)**0.5
  cor = (mean_xy - mean_x * mean_y) / (sigma_x * sigma_y)
  print(f'cor = {cor:.2f}')
  c = ROOT.TCanvas()
  g_px.Draw('ap')
  c.SaveAs('graph.pdf')
  #sleep(1000)

if 0:
  variables = {
    'mcT[0]': 0.,
    'mcTbar[0]': 0.,
    'mcT[0]*mcT[0]': 0.,
    'mcT[0]*mcTbar[0]': 0.,
    'mcTbar[0]*mcTbar[0]': 0.,
  }
  for k in variables:
    t.Draw(f"{k}>>h(1000000,-100000.,100000.)", "", "goff")
    h_mcT_px = ROOT.gDirectory.Get('h')
    variables[k] = h_mcT_px.GetMean()
  print(variables)
  num = variables['mcT[0]*mcTbar[0]'] - variables['mcT[0]'] * variables['mcTbar[0]']
  den = (variables['mcT[0]*mcT[0]'] * variables['mcTbar[0]*mcTbar[0]'])**0.5
  cor = num / den
  print(f'cor = {cor:.2f}')

if 0:
  ROOT.EnableImplicitMT() # parallel
  rdf = ROOT.RDataFrame('tree', [fname]*nrepeat)
  rdf = rdf.Define("x", "mcT[0]").Define("y", "mcTbar[0]").Define("xy", "x*y").Define('x2', 'x*x').Define('y2', 'y*y')
  mean_x = rdf.Mean("x")
  mean_y = rdf.Mean("y")
  mean_xx = rdf.Mean("x2")
  mean_yy = rdf.Mean("y2")
  mean_xy = rdf.Mean("xy")
  num = mean_xy.GetValue() - mean_x.GetValue() * mean_y.GetValue()
  den = ((mean_xx.GetValue() - mean_x.GetValue()**2) * (mean_yy.GetValue() - mean_y.GetValue()**2))**0.5
  cor = num / den
  print(f'cor = {cor:.2f}')
  print(f'number of runs: rdf = {rdf.GetNRuns()}') # should be 1

if 0:
  g_px = ROOT.TGraph()
  g_py = ROOT.TGraph()
  t.SetBranchStatus('*', 0)
  mcNu = array.array('f', [0.]*4)
  t.SetBranchStatus('mcNu', 1)
  t.SetBranchAddress('mcNu', mcNu)
  mcNubar = array.array('f', [0.]*4)
  t.SetBranchStatus('mcNubar', 1)
  t.SetBranchAddress('mcNubar', mcNubar)
  metPx = array.array('f', [0.]*1)
  t.SetBranchStatus('metPx', 1)
  t.SetBranchAddress('metPx', metPx)
  metPy = array.array('f', [0.]*1)
  t.SetBranchStatus('metPy', 1)
  t.SetBranchAddress('metPy', metPy)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    g_px.AddPoint((mcNu[0]+mcNubar[0]), metPx[0])
    g_py.AddPoint((mcNu[1]+mcNubar[1]), metPy[0])
  c = ROOT.TCanvas()
  c.Divide(2)
  c.cd(1)
  g_px.Draw('ap')
  c.cd(2)
  g_py.Draw('ap')
  c.SaveAs('graph.pdf')

if 0:
  t.Draw("(mcNu[0]+mcNubar[0]):metPx")
  sleep(1000)

if 1:
  ROOT.EnableImplicitMT() # parallel
  rdf = ROOT.RDataFrame('tree', [fname]*nrepeat)
  g_px = rdf.Define('TMP', "mcNu[0]+mcNubar[0]").Graph("TMP", "metPx")
  g_py = rdf.Define('TMP', "mcNu[1]+mcNubar[1]").Graph("TMP", "metPy")
  c = ROOT.TCanvas()
  c.Divide(2)
  c.cd(1)
  g_px.GetXaxis().SetTitle('gen. level')
  g_px.GetYaxis().SetTitle('rec. level')
  g_px.Draw('ap')
  c.cd(2)
  g_py.Draw('ap')
  g_py.GetXaxis().SetTitle('gen. level')
  g_py.GetYaxis().SetTitle('rec. level')
  c.SaveAs('graph.png')
  c.SaveAs('graph.pdf')

  rdf = rdf.Define("x", "mcNu[0]+mcNubar[0]").Define("y", "metPx").Define("xy", "x*y").Define('x2', 'x*x').Define('y2', 'y*y')
  mean_x = rdf.Mean("x")
  mean_y = rdf.Mean("y")
  mean_xx = rdf.Mean("x2")
  mean_yy = rdf.Mean("y2")
  mean_xy = rdf.Mean("xy")
  num = mean_xy.GetValue() - mean_x.GetValue() * mean_y.GetValue()
  den = ((mean_xx.GetValue() - mean_x.GetValue()**2) * (mean_yy.GetValue() - mean_y.GetValue()**2))**0.5
  cor = num / den
  print(f'cor = {cor:.2f}')

  print(f'number of runs: rdf = {rdf.GetNRuns()}') # should be 1
