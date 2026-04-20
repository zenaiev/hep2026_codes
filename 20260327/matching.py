# delta^2 = (eta_g-eta_r)^2+(phi_g-phi_r)^2

import ROOT
import array
import tqdm

def matching(genSign, genp4, recN, recPt, recEta, recPhi, h):
  delta_best = -1
  irec_best = -1
  genVector = None
  for irec in range(recN):
    if genSign * recPt[irec] < 0:
      continue
    genVector = ROOT.Math.PxPyPzMVector(genp4[0], genp4[1], genp4[2], genp4[3])
    delta_phi = genVector.Phi()-recPhi[irec]
    if delta_phi > ROOT.TMath.Pi():
      delta_phi = 2 * ROOT.TMath.Pi() - delta_phi
    delta2 = (genVector.Eta()-recEta[irec])**2 + delta_phi**2
    delta = ROOT.TMath.Sqrt(delta2 if delta2 >= 0. else 0.)
    h.Fill(delta)
    if delta_best < 0 or delta < delta_best:
      delta_best = delta
      irec_best = irec
  return irec_best, delta_best, genVector

nrepeat = 1
#nrepeat = 1000
fname = 'ttbarSel_merged.root' # 7980 events, signal ttbar MC
t = ROOT.TChain('tree')
for i in range(nrepeat):
  t.Add(fname)
t.Add('/mnt/d/od/MERGED/ntuples-mc/TTJets_TuneZ2_7TeV-madgraph-tauola/00000/ttbarSel_merged.root')

t.SetBranchStatus('*', 0)

# new TTree
def new_branch(t, branch_name, branch_type, branch_size=1):
  root_branch_type = {'f': 'F', 'i': 'I'}
  br = array.array(branch_type, [0]*branch_size)
  t.Branch(branch_name, br, f'{branch_name}/{root_branch_type[branch_type]}')
  return br

# read TTree
def add_branch(t, branch_name, branch_type, branch_size=1):
  br = array.array(branch_type, [0]*branch_size)
  t.SetBranchStatus(branch_name, 1)
  t.SetBranchAddress(branch_name, br)
  return br

mcLp = add_branch(t, 'mcLp', 'f', 4)
Nel = add_branch(t, 'Nel', 'i', 1)
nleptons_max = 5
elPt = add_branch(t, 'elPt', 'f', nleptons_max)
elEta = add_branch(t, 'elEta', 'f', nleptons_max)
elPhi = add_branch(t, 'elPhi', 'f', nleptons_max)
Nmu = add_branch(t, 'Nmu', 'i', 1)
muPt = add_branch(t, 'muPt', 'f', nleptons_max)
muEta = add_branch(t, 'muEta', 'f', nleptons_max)
muPhi = add_branch(t, 'muPhi', 'f', nleptons_max)
h_el = ROOT.TH1F('h_delta', '', 1000, 0., 10.)
h_mat_el = ROOT.TH1F('h_delta_mat', '', 1000, 0., 10.)
h_mu = ROOT.TH1F('h_delta', '', 1000, 0., 10.)
h_mat_mu = ROOT.TH1F('h_delta_mat', '', 1000, 0., 10.)
delta_max = 0.1

f = ROOT.TFile.Open('matching.root', 'recreate')
f.cd()
t_new_el = ROOT.TTree('tree_matched_el', 'tree_matched_el')
ttree_delta_best_el = new_branch(t_new_el, 'delta_best_el', 'f')
ttree_irec_best_el = new_branch(t_new_el, 'irec_best_el', 'i')
ttree_gen_pt_el = new_branch(t_new_el, 'gen_pt_el', 'f')
ttree_rec_pt_el = new_branch(t_new_el, 'rec_pt_el', 'f')
t_new_mu = ROOT.TTree('tree_matched_mu', 'tree_matched_mu')
ttree_delta_best_mu = new_branch(t_new_mu, 'delta_best_mu', 'f')
ttree_irec_best_mu = new_branch(t_new_mu, 'irec_best_mu', 'i')
ttree_gen_pt_mu = new_branch(t_new_mu, 'gen_pt_mu', 'f')
ttree_rec_pt_mu = new_branch(t_new_mu, 'rec_pt_mu', 'f')

kinvars = {
  'pt': {'nbins': 8, 'binmin': 0.0, 'binmax': 400.0, 'title': 'p_{T} [GeV]'},
  'eta': {'nbins': 24, 'binmin': -2.4, 'binmax': 2.4, 'title': '\\eta'},
  'phi': {'nbins': 24, 'binmin': -ROOT.TMath.Pi(), 'binmax': ROOT.TMath.Pi(), 'title': '\\phi'},
}
particles = [
  'el',
  #'mu', 
  #'je',
]

h2_resp = {f"h_resp_{part}_{kinvar}": ROOT.TH2F(f"h_resp_{part}_{kinvar}", f"h_resp_{part}_{kinvar}", 
                                                kinvars[kinvar]['nbins'], kinvars[kinvar]['binmin'], kinvars[kinvar]['binmax'], 
                                                kinvars[kinvar]['nbins'], kinvars[kinvar]['binmin'], kinvars[kinvar]['binmax']) 
          for part in particles for kinvar in kinvars}
for part in particles:
  for kinvar in kinvars:
    h2_resp[f"h_resp_{part}_{kinvar}"].GetXaxis().SetTitle(f"{kinvars[kinvar]['title']} (gen.)")
    h2_resp[f"h_resp_{part}_{kinvar}"].GetYaxis().SetTitle(f"{kinvars[kinvar]['title']} (rec.)")
def process_response(h2):
  suf = '_'.join(str(h2.GetName()).split('_')[-2:])
  h2_norm = h2.Clone()
  h2_norm.Sumw2()
  nbinsx = h2.GetNbinsX()
  h_gen = ROOT.TH1F(f"h_gen_{suf}", "", nbinsx, h2.GetXaxis().GetBinLowEdge(1), h2.GetXaxis().GetBinLowEdge(1+nbinsx))
  h_gen.GetXaxis().SetTitle(h2.GetXaxis().GetTitle())
  h_gen.GetYaxis().SetTitle('Events')
  nbinsy = h2.GetNbinsY()
  h_rec = ROOT.TH1F(f"h_rec_{suf}", "", nbinsy, h2.GetYaxis().GetBinLowEdge(1), h2.GetYaxis().GetBinLowEdge(1+nbinsy))
  h_rec.GetXaxis().SetTitle(h2.GetYaxis().GetTitle())
  h_rec.GetYaxis().SetTitle('Events')
  h_sta = ROOT.TH1F(f"h_sta_{suf}", "", nbinsx, h2.GetXaxis().GetBinLowEdge(1), h2.GetXaxis().GetBinLowEdge(1+nbinsx))
  h_sta.GetXaxis().SetTitle(h2.GetXaxis().GetTitle())
  h_sta.GetYaxis().SetTitle('Stability/Purity')
  h_pur = ROOT.TH1F(f"h_pur_{suf}", "", nbinsy, h2.GetYaxis().GetBinLowEdge(1), h2.GetYaxis().GetBinLowEdge(1+nbinsy))
  h_pur.GetXaxis().SetTitle(h2.GetXaxis().GetTitle())
  h_pur.GetYaxis().SetTitle('Stability/Purity')
  for ibinx in range(1, h2.GetNbinsX()+1):
    norm = sum(h2.GetBinContent(ibinx, ibiny) for ibiny in range(h2.GetNbinsY()+2))
    h_gen.SetBinContent(ibinx, norm)
    if norm != 0:
      #for ibiny in range(h2.GetNbinsY()):
      for ibiny in range(1, h2.GetNbinsY()+1):
        h2_norm.SetBinContent(ibinx, ibiny, h2.GetBinContent(ibinx, ibiny) / norm)
      if ibinx >= 1 and ibinx <= h2.GetNbinsX():
        h_sta.SetBinContent(ibinx, h2.GetBinContent(ibinx, ibinx) / norm)
  for ibiny in range(1, h2.GetNbinsY()+1):
    norm = sum(h2.GetBinContent(ibinx, ibiny) for ibinx in range(h2.GetNbinsX()+2))
    h_rec.SetBinContent(ibiny, norm)
    if norm != 0:
      h_pur.SetBinContent(ibiny, h2.GetBinContent(ibiny, ibiny) / norm)
  return h2_norm, h_gen, h_rec, h_sta, h_pur

nevents = t.GetEntries()
nevents = min(100000, nevents)
for i in tqdm.tqdm(range(nevents)):
  t.GetEntry(i)
  irec_best_el, delta_best_el, genp4_el = matching(+1, mcLp, Nel[0], elPt, elEta, elPhi, h_el)
  irec_best_mu, delta_best_mu, genp4_mu = matching(+1, mcLp, Nmu[0], muPt, muEta, muPhi, h_mu)
  ttree_delta_best_el[0] = -1
  ttree_irec_best_el[0] = -1
  ttree_delta_best_mu[0] = -1
  ttree_irec_best_mu[0] = -1
  ttree_gen_pt_el[0] = -1
  ttree_rec_pt_el[0] = -1
  ttree_gen_pt_mu[0] = -1
  ttree_rec_pt_mu[0] = -1
  if delta_best_el < delta_max and irec_best_el >= 0:
    h_mat_el.Fill(delta_best_el)
    ttree_delta_best_el[0] = delta_best_el
    ttree_irec_best_el[0] = irec_best_el
    ttree_gen_pt_el[0] = genp4_el.Pt()
    ttree_rec_pt_el[0] = abs(elPt[irec_best_el])
    t_new_el.Fill()
    h2_resp[f"h_resp_el_pt"].Fill(genp4_el.Pt(), elPt[irec_best_el])
    h2_resp[f"h_resp_el_eta"].Fill(genp4_el.Eta(), elEta[irec_best_el])
    h2_resp[f"h_resp_el_phi"].Fill(genp4_el.Phi(), elPhi[irec_best_el])
  if delta_best_mu < delta_max and irec_best_mu >= 0:
    h_mat_mu.Fill(delta_best_mu)
    ttree_delta_best_mu[0] = delta_best_mu
    ttree_irec_best_mu[0] = irec_best_mu
    ttree_gen_pt_mu[0] = genp4_mu.Pt()
    ttree_rec_pt_mu[0] = abs(muPt[irec_best_mu])
    t_new_mu.Fill()
    #h2_resp[f"h_resp_mu_pt"].Fill(genp4_mu.Pt(), muPt[irec_best_mu])
    #h2_resp[f"h_resp_mu_eta"].Fill(genp4_mu.Eta(), muEta[irec_best_mu])
    #h2_resp[f"h_resp_mu_phi"].Fill(genp4_mu.Phi(), muPhi[irec_best_mu])

ROOT.gStyle.SetOptStat(0)
for part in particles:
  c_resp = ROOT.TCanvas('c_resp', 'Response matrix', 600, 600)
  c_resp.Divide(3,3)
  for ikinvar, kinvar in enumerate(kinvars):
    c_resp.cd(ikinvar+1)
    h2_resp_norm, h_gen, h_rec, h_sta, h_pur, = process_response(h2_resp[f"h_resp_{part}_{kinvar}"])
    h2_resp_norm.Draw('colztext')
    c_resp.cd(ikinvar+4)
    ROOT.gPad.SetLogy()
    h_gen.SetLineColor(1)
    h_gen.Draw('hist')
    h_rec.SetLineColor(4)
    h_rec.Draw('hist same')
    legend1 = ROOT.TLegend(0.65, 0.75, 0.9, 0.9)
    legend1.AddEntry(h_gen, 'True', 'l')
    legend1.AddEntry(h_rec, 'Reco', 'l')
    legend1.Draw()
    c_resp.cd(ikinvar+7)
    h_sta.SetLineColor(1)
    h_sta.SetMinimum(0)
    h_sta.SetMaximum(1.1)
    h_sta.Draw('hist')
    h_pur.SetLineColor(4)
    h_pur.Draw('hist same')
    legend2 = ROOT.TLegend(0.15, 0.15, 0.3, 0.25)
    legend2.AddEntry(h_sta, 'Stability', 'l')
    legend2.AddEntry(h_pur, 'Purity', 'l')
    legend2.Draw()
  c_resp.SaveAs(f'response_{part}.pdf')
  c_resp.SaveAs(f'response_{part}.png')

f.cd()
t_new_el.Write()
t_new_mu.Write()

c = ROOT.TCanvas('c', '', 600, 600)
c.Divide(2)
h_mat = [h_mat_el, h_mat_mu]
for ih,h in enumerate([h_el, h_mu]):
  c.cd(ih+1)
  ROOT.gPad.SetLogx()
  ROOT.gPad.SetLogy()
  h.Draw()
  h_mat[ih].SetLineColor(2)
  h_mat[ih].SetMarkerColor(2)
  h_mat[ih].SetMarkerStyle(8)
  #if ih == 0:
  h_mat[ih].Draw('p same')
for ext in ['pdf', 'png']:
  c.SaveAs(f'matching.{ext}')
