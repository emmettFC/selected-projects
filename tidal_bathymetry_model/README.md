# Tidal Bathymetry Model & Review of applied methods 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/tidal_bathymetry_model/assets_README/bathy_12.png)

## Introduction

Methods for estimating bathymetry from multispectral images can be broadly classified as either empirical or physical (5). Physical models use known properties of light attenuation in water, substrate reflectance, and diffuse attenuation related to suspended concentrations of biogenic constituents—such as chlorophyll, suspended sediment or dissolved organic matter—to estimate depth from spectral values. Empirical models use known depth values to ‘train’ predictive functions of the relationship between spectral values and depth (5). Models of the latter category are typically hybrid physical-empirical models, and employ some theoretical model of bathymetry to make baseline predictions which are then corrected based on the observed error between depth estimates and ground truth. In the first section I will review the application of two known Bathymetric estimation models to WV2 imagery of the South Water Cay Marine preserve in Belize, and in the second section I will review some preliminary work towards a proposed modification of the Lyzenga Bathymetric estimation technique using drone imagery and a sequential tidal correction. 

## Part I: Review of applied methods for WV2 images of South Water Cay Marine Preserve, Belize 

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
+
The chlorophyll fluorescence readings used to validate the model are taken at a discrete point in the (x, y) space at a depth of 1 meter from the surface (17). The assumption of uniformity in the (x, y) plane parallel to the surface is made to eliminate the impact of horizontal transport / advection of plankton during the tidal cycle. This assumption follows from the empirical observation that changes in salinity and temperature are dominated by the 12 hour semidiurnal tidal cycle, though remain relatively stable through the 6 hour tidal current cycle (8). This observation comes from the paper below:

```
Dancing with the Tides: Fluctuations of Coastal Phytoplankton Orchestrated by Different Oscillatory Modes of the Tidal Cycle.
Blauw AN, Beninca` E, Laane RWPM, Greenwood N, Huisman J (2012)
PLoS ONE 7(11): e49319. doi:10.1371/journal.pone.0049319
```

Further the assumption of (x,y) planar uniformity allows for the proposition of a specific discrete state space in the (z) direction, which will make a solution by finite difference methods possible. The model will describe the change in plankton density at 1m spatial steps in the (z) direction, and at 1-second time steps through the tidal-current period of ~6 hours. The three dimensional distribution (x, y, z) of plankton within each 1m section of the water column at any time (t) will be assumed to be uniform. The concentration P(z, t) of plankton at depth (z) and time (t) will be the output of the model at each step in time, though it is the concentration P(t(n), zmax) in the top 1 meter of the water column that is of specific interest given the availability of empirical data. 


### Model derivation

#### Simple one dimensional diffusion over infinite domain (no boundary conditions)

The base of the model is a one dimensional diffusion equation—Fickian diffusion or the heat equation—which describes the random motion of particles in a Newtonian fluid caused by unresolved turbulence or agitation (19). The equation is expressed as the following partial differential equation given by equation (1) below. This equation is not solvable analytically, though it can be solved numerically for the variable concentration P(z, t) given known parameters for D and sufficient boundary conditions (3)(19)(20). The left-hand expression is of order 1 in time, and therefore requires a single boundary condition for t=0 at each interval in z. The right-hand expression is a second order spatial derivative, and therefore requires two boundary conditions at either edge of the domain {x=0, x=dx(n)(19). Boundary conditions and initialization of parameters will be discussed bellow. The simplest and most intuitive method of solving this equation numerically is to use a forward in time centered in space (FTCS) finite difference method(19). This method allows you to discretize the problem in space and time by representing the right and left side as finite differences using Taylor expansions. The left-hand temporal derivative is thus restated and rearranged for P’(x, t). The FTCS approximation for the heat equation is given by equation (2) below. 

   ![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plankton_image_set_final_1.png)


In this implementation of the FTCS scheme I have not considered the error terms O(dt) and have disregarded the higher order terms. This is the baseline equation (equation (2)) that is used to build the model for this project, and can be used to describe the sequential change of concentration of particles specified by P(z, t +dt) at each step in time dt.

#### Simple one dimensional diffusion with sedimentation over infinite domain (no boundary conditions)

The one dimensional diffusion equation can be easily modified to incorporate a sedimentation term (10). This term is intended to describe the constant sinking of plankton due to gravity. Planktonic sinking is a well-studied phenomenon, and sinking rates for various species of plankton are correspondingly well documented. A study of suspended macro benthic gradients in submarine caves used a 2-dimensional diffusion-sedimentation model to describe the observed distribution of plankton perpendicular to the mouth of the cave(10). To parameterize the sinking term, the authors used a range of sedimentation rates between 10^-6 and 10^-3. I have experimented with a range of sinking rates based on the species of plankton common the region of the North Sea described by the empirical data (8):

    * Chaeotoceros 
    * Paralia
    * Skeletonema
    * Eucampia
    * Cylindrotheca
    * Plagiogrammopsis

The relatively higher concentration of benthic diatoms in this region requires a higher range of sinking rates, between 10^-5 and 10^-2 ms^-1(8). The continuous one dimensional diffusion equation with a sedimentation term is given  by equation (3). To incorporate the sedimentation term into the FTCS approximation, the first order spatial derivative must be replaced with the central difference approximation of the first derivative. Recall that this is the difference of the backward and forward difference approximations at P(x,z-1) and P(x,z+1), as given by the Taylor expansions. The sedimentation term then can be replaced by the expression given in equation (4). Equation 5 gives the FTCS approxiation of the one dimensional diffusion equation ammended to include the descretized sedimentation term from equation 4. 

The units of Ws are ms^-1, the units of dz are ms^-1, and the units of the concentration P(z,t) are mass(m^-3), so the expression has units mass(m^-3). This is the same as the units of the D * the second spatial derivative, and since the two terms are summed the resulting expression has the correct units. It is illustrative to compare the results of a simulation of this model with the previous diffusion equation. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/sed-and-nosed-graphs.png)

The lefthand plot following shows the output of the model when initialized with two symmetric concentrations (in magnitude and space) at t=0. In the righthand figure, the initial condition of symmetrical peaks flattens out from the maximum of the function on both sides as in the diffusion model, though now the peaks also shift towards the bottom. This is a pretty satisfying result, because what is being illustrated in this graph—and by this model—is the gradual diffusive spreading out of particles in the water column with a simultaneous constant downward drift or sedimentation. This is intuitively what I imagine the motion of suspended plankton would look like in fluid completely free of turbulent forcing. This is then a kind of ‘null model’ of the latent physical movement of plankton, and sets up the next step of adding in a periodic excitation to mimic the cycle of tidal current velocity. 

#### Simple one dimensional diffusion with sedimentation and periodic excitation

Initially I intended to model the vertical fluctuation of plankton as a periodic upward velocity proportional to the tidal current speed. This is however not a physically meaningful approach, since the vertical component of velocity in this context is the result of turbulent mixing / diffusivity that propagates both upward and downward(21). It is therefore preferable to build the periodicity into the model through a spatiotemporal variability in the diffusion coefficient D. This is slightly more challenging than the addition of sedimentation though is ultimately pretty straightforward. The second set of equations given below describe this process: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plankton_eq_final_2.png)

The first step is to change the constant D in the model to a function of time and space D(z, t). The addition of D(z, t) yields the expression given by equation 6. The left hand expression is already known by the forward difference approximation, though the right hand expression now has to be expanded by the chain rule. Applying the chain rule to the right hand expression we then get the expression given by equation 7. We now combine equation 7 with the descrete sedimentation term given by equation 4, and are left with expressions for D'(z,t)(partialP/partialz), D(z,t)(partial^2p/partialz^2) and Ws(partialp/partialz). The FTCS approxiamtions of each term are given by equations 8, 9 & 10. They are combined symbolically resulting in the final equation for this model espression by equation 11 above. Finally, the expression for D(z,t) must be specified: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plankton_eq_final_3.png)

The point of expressing D as a function is to allow it to vary along with the fluctuation in tidal current speed. To simplify this, I make the assumption that at t=0 the tide is at its high or low extreme, and therefore the derivative of tidal height, or current velocity, is 0. Based on some trial and error, and consideration of the physical context, I chose to represent the function D(z, t) as given by equation 12 above given parameters (zbar = zmean; z = zn; e=proportionality constant; zbar(t;t=0) the initial concentration at zmean or zbar).

Practicallt, the value of D will vary according to both 1) the tidal current velocity at time t, and 2) the distance from the mean value of z or the middle of the water column. The latter dimension of diffusive variation is based on the principle of wall-bounded diffusion (21), which in the most crude interpretation holds that the magnitude of diffusive velocity is inversely related to the distance between a point and a solid boundary. For the sake of simplicity I am considering that the surface of the water and the sea floor are both equivalently static boundaries, and therefore the proportional relationship of D and z is symmetric about the average value of z (zmean). The value (e) or the constant of proportionality can be adjusted to bring about the desired relationship between D and Ws over time. At t=0, the sinusoidal term goes to zero and at z=zmean the function f(zmean, z) is at its maximum value of 1. Therefore D(zmean, 0) = v_min_zmean, and is the maximum value in the vector of D(zn, t=0) used to initialize the forward integration of the equation. The initial vector for D(zn, t=0) is pictured below: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/i-density-vector-plank.png)

In order for the model to make consistent sense, the units of D(z,t) have to be the same as the constant D, m^2s^-1. Conveniently, the units of f(zmean, z) are meters, and therefore the function D(z,t)  is of units m^2s^-1, so it works out in the larger equation. A few more considerations have to be made before the model is in a workable form. First, the issue of the boundary conditions. When you plot the concentration SUM(P(zn, t)) for each time step, the impact of infinite domain on the model performance is very clear: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/loss-of-mass-plankton-.png)

To avoid this loss of mass, I specified a impermeable boundary condition at the sea floor, or z=0, such that D(z=0,t) = -D(dP/dt) (19). This acts as an equal and opposite diffusive force at the low boundary, such that there is an effect of accumulation at the lower boundary. This improves the model both by retaining mass, but also bring the representation closer to the physical reality of particle sedimentation and suspension. 

Finally, the model requires that parameters for d_initial (v_min_zmean) and (e) be chosen. The range of acceptable values for D is constrained by the value of dz and dt. The Courant–Friedrichs–Lewy condition states that D <= dx^2/2dt, or the model will be unstable in time (24). With D=0.5 for dz,dt =1 the model yields negative concentrations. If you set the diffusion coefficient to 1, the model concentrations are completely nonsensical. All this to say that the values for d_initial (v_min_zmean) and (e) were chosen such that at the peak of tidal current speed (for t divisible by 10800 seconds and not 21600), the maximum positional value of D(z,t), which is at z=zmean, will be equal to 0.5. To satisfy this, the values for d_initial and (e) were both set to 0.25. Further, this is defensible parameterization because this means that on average, Ws is an order of magnitude less than D(z,t), which is appropriate given the empirical range of values for those parameters presented in the literature (8)(10).  When this is all put together, the function to iterate is actually quite simple: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_code_segment_final.png)

This equation is not a particularly heavy operation and was straightforward to simulate. I ran the model for 10 cycles of 21600 time steps, which corresponds to 10 cycles of the tidal current period of 6 hours. 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/density-plank-difsed-final.png)

The top lefthand subplot shows the initial symmetric punctuated release (black), at the minimum of tidal current velocity, and then for each subsequent six hour period the density distribution at the max current speed (blue) and min current speed (red). Perhaps unreasonably the model instantly reaches an oscilatory state of periodic excitation once the initial density concentration has diffused towards the upper and lower buondary. The three conditions (initial, max current, min current) plotted in three dimensions with the same color convention is shown below: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/plank-3d-density.png)

When you isolate the top one meter of the water column, you can see a very regular periodic change in density as desired by the model: 

![alt text](https://github.com/emmettFC/selected-projects/blob/master/plankton_model/assets_README/_plank_9.png)


