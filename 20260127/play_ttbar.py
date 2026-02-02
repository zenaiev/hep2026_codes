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
if 1:
  t.SetBranchStatus('*', 0)
  mcLp = array.array('f', [0.]*4)
  t.SetBranchStatus('mcLp', 1)
  t.SetBranchAddress('mcLp', mcLp)
  mcLm = array.array('f', [0.]*4)
  t.SetBranchStatus('mcLm', 1)
  t.SetBranchAddress('mcLm', mcLm)
  selected = 0
  for i in range(t.GetEntries()):
    #t.mcLp # accessing TTree data this way is VERY SLOW
    t.GetEntry(i)
    if ROOT.TMath.Sqrt(mcLp[0]**2+mcLp[1]**2)>20. and ROOT.TMath.Sqrt(mcLm[0]**2+mcLm[1]**2)>20.:
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
