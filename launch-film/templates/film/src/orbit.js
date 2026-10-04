/* ORBIT: original procedural 3D motion study, authored for this film.
   Portable software renderer: real 3D geometry, camera projection, surface normals,
   depth ordering and lighting; no external engine or creator artwork. */
(function(){
const TAU=Math.PI*2,dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2],sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]],unit=a=>{let n=Math.hypot(...a);return a.map(x=>x/n)},cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function rot(v,ax,ay,az){let [x,y,z]=v,c=Math.cos(ax),s=Math.sin(ax);[y,z]=[y*c-z*s,y*s+z*c];c=Math.cos(ay);s=Math.sin(ay);[x,z]=[x*c+z*s,-x*s+z*c];c=Math.cos(az);s=Math.sin(az);return[x*c-y*s,x*s+y*c,z]}
function grid(fn,nu,nv){let faces=[];for(let i=0;i<nu;i++)for(let j=0;j<nv;j++){let pts=[[i,j],[i+1,j],[i+1,j+1],[i,j+1]].map(([u,v])=>fn(u/nu,v/nv).p),m=fn((i+.5)/nu,(j+.5)/nv);faces.push({p:pts,c:m.p,n:m.n});}return faces}
function sphere(radius,nu=64,nv=36){return grid((u,v)=>{let a=u*TAU,b=v*Math.PI,n=[Math.sin(b)*Math.cos(a),Math.cos(b),Math.sin(b)*Math.sin(a)];return{p:n.map(x=>x*radius),n}},nu,nv)}
function torus(r,t){return grid((u,v)=>{let a=u*TAU,b=v*TAU,ca=Math.cos(a),sa=Math.sin(a),cb=Math.cos(b),sb=Math.sin(b);return{p:[(r+t*cb)*ca,t*sb,(r+t*cb)*sa],n:[cb*ca,sb,cb*sa]}},160,12)}
window.makeOrbit=function(){
 const canvas=document.createElement('canvas');canvas.width=1600;canvas.height=900;const ctx=canvas.getContext('2d');
 const meshes=[{faces:sphere(.97),ax:0,az:0,col:[8,50,216],metal:.42},{faces:torus(2.05,.11),ax:.65,az:.31,col:[210,222,237],metal:.91},{faces:torus(1.57,.064),ax:-.9,az:.9,col:[12,76,255],metal:.62},{faces:torus(2.72,.014),ax:.24,az:-.6,col:[141,176,224],metal:.65},{faces:torus(1.10,.024),ax:1.45,az:0,col:[180,207,246],metal:.72}];
 const sat=sphere(.23,30,20),satSmall=sphere(.11,20,12);
 const windowDirection=unit([-.6,.85,.5]);
 const keys=[{e:[5.7,3.1,7.8],f:40},{e:[-5.9,2.1,6.6],f:36},{e:[-3.2,6.6,6.6],f:40},{e:[4.8,2.0,8.4],f:40}],L=unit([-4,7,5]);
 function render(time,progress=0){
  let p=Math.max(0,Math.min(2.9999,progress*3)),k=Math.floor(p),u=p-k,s=u*u*(3-2*u),a=keys[k],b=keys[k+1],eye=a.e.map((x,i)=>x+(b.e[i]-x)*s),fov=a.f+(b.f-a.f)*s,F=unit(eye.map(x=>-x)),R=unit(cross(F,[0,1,0])),U=cross(R,F),fl=450/Math.tan(fov*Math.PI/360),root=.22+time*.13;
  let tris=[];
  function proj(v){let d=sub(v,eye),z=dot(d,F);return[800+dot(d,R)*fl/z,450-dot(d,U)*fl/z,z]}
  function gather(faces,ax,az,col,metal,translate=[0,0,0]){
   const m0=rot(rot([1,0,0],ax,0,az),0,root,.13),m1=rot(rot([0,1,0],ax,0,az),0,root,.13),m2=rot(rot([0,0,1],ax,0,az),0,root,.13),tr=rot(translate,0,root,.13);
   function trans(v,normal=false){return [0,1,2].map(i=>m0[i]*v[0]+m1[i]*v[1]+m2[i]*v[2]+(normal?0:tr[i]))}
   for(let face of faces){let center=trans(face.c),N=trans(face.n,true),V=unit(sub(eye,center)),nv=dot(N,V);if(nv<=.015)continue;let q=face.p.map(v=>proj(trans(v))),z=q.reduce((a,v)=>a+v[2],0)/4;
    let d=Math.max(0,dot(N,L)),H=unit(V.map((x,i)=>x+L[i])),spec=Math.pow(Math.max(0,dot(N,H)),45),fres=Math.pow(1-nv,3),reflect=V.map((x,i)=>2*nv*N[i]-x),window=Math.pow(Math.max(0,dot(reflect,windowDirection)),13),env=.25+.63*Math.max(0,Math.min(1,(reflect[1]+.5)/1.1));
    let rgb=col.map((x,i)=>Math.max(0,Math.min(255,x*(metal*env+(1-metal)*(.30+d*.67))+spec*145+fres*(i===0?26:i===1?37:56)+window*75*metal)));
    tris.push({q,z,color:`rgb(${rgb[0]|0},${rgb[1]|0},${rgb[2]|0})`});
   }
  }
  for(let m of meshes)gather(m.faces,m.ax,m.az,m.col,m.metal);
  for(let i=0;i<4;i++){let angle=time*.25+i*TAU/4,r=i%2===0?2.05:2.72,center=rot([Math.cos(angle)*r,.10,Math.sin(angle)*r],i%2===0?.65:.24,0,i%2===0?.31:-.6);gather(i===0?sat:satSmall,0,0,i===0?[219,228,245]:[8,53,219],.71,center)}
  tris.sort((a,b)=>b.z-a.z);ctx.clearRect(0,0,1600,900);ctx.lineJoin='round';ctx.lineWidth=.45;
  for(let f of tris){ctx.beginPath();f.q.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle=f.color;ctx.strokeStyle=f.color;ctx.fill();ctx.stroke();}
  return canvas;
 }
 return{canvas,render,dispose(){}};
};
})();
