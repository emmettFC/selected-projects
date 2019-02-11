# Simple physical plankton model
## Describing coastal plankton density with a one dimensional diffusion-sedimentation model with spatially variable diffusion coefficient and sinusoidal excitation

### Introduction

This aim of this project is to develop a model that describes the variability of plankton density in-phase with the tidal current cycle of ~6 hours and 12 minutes. The model is intended to describe a short-duration localized periodicity of near-surface (top 1m) plankton density in terms of variable tidal current velocity. The behavior of the model will be compared to empirical data provided by 

   * a SMartBuoy deployed in the Warp station estuary in the North Sea by the Center for Environment Fisheries and Aquaculture Science          (CEFAS) and 
   * tidal gauge data from the nearby Sheerness station collected by the British Oceanographic Data Center (BODC)(8)(17)(18) 

The Warp station in the North Sea is located in a shallow tidal inlet, with stable depth of 15 meters and tidal range of 4.3 meters (8)(17). The water column is well mixed due to its shallow depth and turbulent mixing as a result of tidal current. The proposed model will make several simplifying assumptions, which follow from the short-duration temporal scale of the research question and the characteristics of the empirical context that is being explored. The model will assume the following: 

   * there will be no loss of plankton due to grazing or death; 
   * there will be no growth of plankton due to photosynthesis; 
   * at any time (t) the horizontal (x, y) distribution of plankton density will be assumed to be uniform in the inlet; 
   * there will be no consideration of changes in density corresponding to the change in volume due to rise and fall of the water              level; 
   * tidal current velocity will be treated as a laminar force perpendicular to the mouth of the inlet (10)
  
The model then seeks only to describe variability in the vertical (z) distribution of plankton density in the water column as a consequence of periodic laminar flow velocity. 

The chlorophyll fluorescence readings used to validate the model are taken at a discrete point in the (x, y) space at a depth of 1 meter from the surface (17). The assumption of uniformity in the (x, y) plane parallel to the surface is made to eliminate the impact of horizontal transport / advection of plankton during the tidal cycle. This assumption follows from the empirical observation that changes in salinity and temperature are dominated by the 12 hour semidiurnal tidal cycle, though remain relatively stable through the 6 hour tidal current cycle (8). This observation comes from the paper below:

```
Dancing with the Tides: Fluctuations of Coastal Phytoplankton Orchestrated by Different Oscillatory Modes of the Tidal Cycle.
Blauw AN, Beninca` E, Laane RWPM, Greenwood N, Huisman J (2012)
PLoS ONE 7(11): e49319. doi:10.1371/journal.pone.0049319
```

Further the assumption of (x,y) planar uniformity allows for the proposition of a specific discrete state space in the (z) direction, which will make a solution by finite difference methods possible. The model will describe the change in plankton density at 1m spatial steps in the (z) direction, and at 1-second time steps through the tidal-current period of ~6 hours. The three dimensional distribution (x, y, z) of plankton within each 1m section of the water column at any time (t) will be assumed to be uniform. The concentration P(z, t) of plankton at depth (z) and time (t) will be the output of the model at each step in time, though it is the concentration P(t(n), zmax) in the top 1 meter of the water column that is of specific interest given the availability of empirical data. 


### Model derivation

#### Simple one dimensional diffusion over infinite domain (no boundary conditions)

The base of the model is a one dimensional diffusion equation—Fickian diffusion or the heat equation—which describes the random motion of particles in a Newtonian fluid caused by unresolved turbulence or agitation (19). The equation is expressed as the following partial differential equation: 

   ![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_eq_1.png)

This equation is not solvable analytically, though it can be solved numerically for the variable concentration P(z, t) given known parameters for D and sufficient boundary conditions (3)(19)(20). The left-hand expression is of order 1 in time, and therefore requires a single boundary condition for t=0 at each interval in z. The right-hand expression is a second order spatial derivative, and therefore requires two boundary conditions at either edge of the domain {x=0, x=dx(n)(19). Boundary conditions and initialization of parameters will be discussed bellow. The simplest and most intuitive method of solving this equation numerically is to use a forward in time centered in space (FTCS) finite difference method(19). This method allows you to discretize the problem in space and time by representing the right and left side as finite differences using Taylor expansion. The left-hand temporal derivative is thus restated and rearranged for P’(x, t): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_2_eq2.png)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_3_eq3.png)

This is the forward difference approximation of the temporal derivative using the Taylor expansion(19). In my implementation of the FTCS scheme I have not considered the error term O(dt) and have disregarded the higher order terms. The central difference approximation for the right hand second order spatial derivative can be derived as follows: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_4_eq_4.png)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_5_eq_5.png)

From the first expression you can get the forward difference approximation as above for the time step t + dt but instead for z + dz, and the second yields the backwards difference approximation. Subtracting the backward difference approximation from the forward approximation, you get the central difference approximation for the first order spatial term(19). When you then add the backward and forward difference approximations you get an expression for the second order spatial term: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_6_eq_6.png)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_7_eq_7.png)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_8_eq8.png)

The terms on the end are truncation errors resulting from the discretization of the continuous diffusion equation. This error can become cumulatively significant in long-term model simulations. A more formal consideration of truncation error is something that would benefit the model proposed here given more time. These errors will not be considered in the remainder of this analysis. Substituting in the forward difference expression for the first order temporal derivative on the left, and the central difference approximation of the second order spatial term on the right, gives the FTCS approximation of the one dimensional diffusion equation(20)(19): 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_9_eq9.png)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_10_eq_10.png)

This is the baseline equation that is used to build the model for this project, and can be used to describe the sequential change of concentration of particles specified by P(z, t +dt) at each step in time dt. This FTCS approximation of the diffusion equation specified above was easily transcribed into pure python and simulated for different time increments with the following function: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_1.png)

The results that are produced by this method are dependent on the initialization of parameters (P(zn, t) vector for t=0 and z in (0, ndz)), and the selection of the diffusion coefficient D. Often this solution is demonstrated with a single punctuated release, meaning that the initial concentration vector at t=0 is a zero vector with one component not equal to zero from which the concentration spreads (v0 = [0,0,0,40,0,0,0]) (19)(3). The situation I am trying to model takes in some distribution of plankton density P0 at t=0, which is then redistributed throughout the water column in (z) through the 6 hour tidal current cycle. This redistribution occurs with no loss of plankton mass, which is the effect of the assumption of uniform distribution of plankton density in the (x, y) plane (meaning that horizontal advection through the tidal cycle does not change the vertical gradient since it is the same throughout the inlet).  I mention this because an initialization with a single punctuated release is not representative of this variable initial density distribution P0. For this reason I experimented with multiple punctuated release points of varying magnitudes and spacing. The following is a plot of the model when initialized with two symmetric concentrations (in magnitude and space) at t=0: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_2.png)

#### Simple one dimensional diffusion with sedimentation (no boundary conditions)

The one dimensional diffusion equation can be easily modified to incorporate a sedimentation term (10). This term is intended to describe the constant sinking of plankton due to gravity. Planktonic sinking is a well-studied phenomenon, and sinking rates for various species of plankton are correspondingly well documented. A study of suspended macro benthic gradients in submarine caves used a 2-dimensional diffusion-sedimentation model to describe the observed distribution of plankton perpendicular to the mouth of the cave(10). To parameterize the sinking term, the authors used a range of sedimentation rates between 10^-6 and 10^-3. I have experimented with a range of sinking rates based on the species of plankton common the region of the North Sea described by the empirical data (8):

    * Chaeotoceros 
    * Paralia
    * Skeletonema
    * Eucampia
    * Cylindrotheca
    * Plagiogrammopsis

The relatively higher concentration of benthic diatoms in this region requires a higher range of sinking rates, between 10^-5 and 10^-2 ms^-1(8). The continuous one dimensional diffusion equation with a sedimentation term is as follows: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_11_eq_11.png)

To incorporate the sedimentation term into the FTCS approximation, the first order spatial derivative must be replaced with the central difference approximation of the first derivative. Recall that this is the difference of the backward and forward difference approximations at P(x,z-1) and P(x,z+1), as given by the Taylor expansions. The sedimentation term then can be replaced by the expression: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/12_eq_12.png)

The units of Ws are ms^-1, the units of dz are ms^-1, and the units of the concentration P(z,t) are mass(m^-3), so the expression has units mass(m^-3). This is the same as the units of the D * the second spatial derivative, and since the two terms are summed the resulting expression has the correct units. It is illustrative to compare the results of a simulation of this model with the previous diffusion equation. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_3.png)

The initial condition of symmetrical peaks flattens out from the maximum of the function on both sides as in the diffusion model, though now the peaks also shift towards the bottom. This is a pretty satisfying result, because what is being illustrated in this graph—and by this model—is the gradual diffusive spreading out of particles in the water column with a simultaneous constant downward drift or sedimentation. This is intuitively what I imagine the motion of suspended plankton would look like in fluid completely free of turbulent forcing. This is then a kind of ‘null model’ of the latent physical movement of plankton, and sets up the next step of adding in a periodic excitation to mimic the cycle of tidal current velocity. 

#### Simple one dimensional diffusion with sedimentation and periodic excitation

Initially I intended to model the vertical fluctuation of plankton as a periodic upward velocity proportional to the tidal current speed. This is however not a physically meaningful approach, since the vertical component of velocity in this context is the result of turbulent mixing / diffusivity that propagates both upward and downward(21). It is therefore preferable to build the periodicity into the model through a spatiotemporal variability in the diffusion coefficient D. This is slightly more challenging than the addition of sedimentation though is ultimately pretty straightforward. The first step is to change the constant D in the model to a function of time and space D(z, t). For simplicity of representation—and since it does not have impact on the ultimate expression—I will disregard sedimentation in the derivation. The addition of D(z, t) yields the following from the first diffusion equation: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/13_eq_13.png)

The left hand expression is already known by the forward difference approximation, though the right hand expression now has to be expanded by the chain rule. Applying the chain rule to the right hand expression we then get: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_14_eq_15.png)

We have already found an expression for dP/dZ, so the only thing to do is to discretize D’(z,t). D can be treated exactly as the spatial components of dP/dz, approximating central difference with a Taylor expansion: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_15_eq_15.png)

The one dimensional diffusion equation with variable diffusion coefficient is approximated as: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/16_eq16.png)

The complete model form for this analysis is the above diffusion model with variable diffusion coefficient and the sedimentation term as specified in the last section (which can just be added on to the end of the above). The point of expressing D as a function is to allow it to vary along with the fluctuation in tidal current speed. To simplify this, I now make the assumption that at t=0 the tide is at its high or low extreme, and therefore the derivative of tidal height, or current velocity, is 0. Based on some trial and error, and consideration of the physical context, I chose to represent the function D(z, t) as: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_17_eq_17.png)

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_18_eq_18.png)

The value of D will vary according to both 1) the tidal current velocity at time t, and 2) the distance from the mean value of z or the middle of the water column. The latter dimension of diffusive variation is based on the principle of wall-bounded diffusion (21), which in the most crude interpretation holds that the magnitude of diffusive velocity is inversely related to the distance between a point and a solid boundary. For the sake of simplicity I am considering that the surface of the water and the sea floor are both equivalently static boundaries, and therefore the proportional relationship of D and z is symmetric about the average value of z (zmean).

There are several other parameters to note in the above expressions. The value (e) is the constant of proportionality, and can be adjusted to bring about the desired relationship between D and Ws over time. The value v_min_mean is the initial value D(z,t) for z=zmean and t=0. At t=0, the sinusoidal term goes to zero and at z=zmean the function f(zmean, z) is at its maximum value of 1. Therefore D(zmean, 0) = v_min_zmean, and is the maximum value in the vector of D(zn, t=0) used to initialize the forward integration of the equation. The initial vector for D(zn, t=0) is pictured below: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_4.png)



