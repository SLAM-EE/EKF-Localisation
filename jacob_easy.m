%pkg load symbolic
function jacob_easy() 
    syms px py vx vy real
    jacobian([sqrt(px^2 + py^2), atan(py/px)],[px, py, vx, vy])
end
%sancho
