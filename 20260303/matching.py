# delta^2 = (eta_g-eta_r)^2+(phi_g-phi_r)^2

import ROOT
import array

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

for i in range(t.GetEntries()):
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
  if delta_best_mu < delta_max and irec_best_mu >= 0:
    h_mat_mu.Fill(delta_best_mu)
    ttree_delta_best_mu[0] = delta_best_mu
    ttree_irec_best_mu[0] = irec_best_mu
    ttree_gen_pt_mu[0] = genp4_mu.Pt()
    ttree_rec_pt_mu[0] = abs(muPt[irec_best_mu])
    t_new_mu.Fill()

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
