# need to download file MERGED/ntuples-mc/TTJets_TuneZ2_7TeV-madgraph-tauola/010003/ttbarSel_merged.root
# via this link: https://cernbox.cern.ch/s/UmbXF1XxVrT4whQ
# or download it from git https://github.com/zenaiev/hep2026_codes/20260127/ttbarSel_merged.root

import ROOT
import array
import time

nrepeat = 1
#nrepeat = 10000
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
  mcT = array.array('f', [0.]*4)
  t.SetBranchStatus('mcLp', 1)
  t.SetBranchAddress('mcLp', mcT)
  mcTbar = array.array('f', [0.]*4)
  t.SetBranchStatus('mcLm', 1)
  t.SetBranchAddress('mcLm', mcTbar)
  selected = 0
  for i in range(t.GetEntries()):
    #t.mcLp # accessing TTree data this way is VERY SLOW
    t.GetEntry(i)
    if ROOT.TMath.Sqrt(mcT[0]**2+mcT[1]**2)>20. and ROOT.TMath.Sqrt(mcTbar[0]**2+mcTbar[1]**2)>20.:
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

if 1:
  # calculate correlation between px(t)[x] and px(tbar)[y]
  # part1 + part2 = top + antitop [LO] + q,g,... [proton remnant + radiation beyond LO]
  # px(part1) = px(part2) = 0 [at LO]
  # px(top) + px(antitop) = px(part1) = px(part2) = 0 [at LO]
  # py(top) + py(antitop) = py(part1) = py(part2) = 0 [at LO]
  t.SetBranchStatus('*', 0)
  mcT = array.array('f', [0.]*4)
  t.SetBranchStatus('mcT', 1)
  t.SetBranchAddress('mcT', mcT)
  mcTbar = array.array('f', [0.]*4)
  t.SetBranchStatus('mcTbar', 1)
  t.SetBranchAddress('mcTbar', mcTbar)
  mean_x = 0
  mean_y = 0
  mean_xx = 0
  mean_yy = 0
  mean_xy = 0
  n = t.GetEntries()
  for i in range(n):
    t.GetEntry(i)
    mean_x += mcT[0]
    mean_y += mcTbar[0]
    mean_xx += mcT[0]**2
    mean_yy += mcTbar[0]**2
    mean_xy += mcT[0]*mcTbar[0]
  mean_x /= n
  mean_y /= n
  mean_xx /= n
  mean_yy /= n
  mean_xy /= n
  sigma_x = (mean_xx - mean_x**2)**0.5
  sigma_y = (mean_yy - mean_y**2)**0.5
  cor = (mean_xy - mean_x * mean_y) / (sigma_x * sigma_y)
  print(f'cor = {cor:.2f}')




#time.sleep(10000)

# imperative style:
# C++
#std::vector<float> v = {1., 2., 3.};
#float sum = 0.;
#for(int i = 0; i < v.size(); i++) {
#  sum += v[i];
#}
#
# declrative style:
#float sum = 0.;
#std::accumulate(v.begin(), v.end(), sum)
