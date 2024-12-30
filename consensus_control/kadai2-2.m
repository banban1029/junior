clc;
clear;
close all;

% Simulation parameters
dt = 0.1; % Time step [s]
T = 30; % Total simulation time [s]
times = 0:dt:T;

% Robot parameters
N = 5; % Number of robots
D = 3; % Collision avoidance distance [cm]
Do = 20; % Obstacle sensing range [cm]

% Control gains
kv = 4;
kvr = 10;
ko = 3000;
sigma = 49;
v_star = [0; 15];

% Formation reference points
r_star = [0, 20; -20/sqrt(3), 0; 20/sqrt(3), 0; -40/sqrt(3), -20; 40/sqrt(3), -20]';

% Initial states (x, y, theta)
states = [105, 16, pi/2;
          88.5, -3, pi/2;
          111.5, -5, pi/2;
          77, -34, pi/2;
          123.1, -24, pi/2]';

% Obstacle positions (Adjusted to higher positions)
obstacles = [100, 300;
             150, 350;
             200, 400]';
obstacle_radii = [20, 20, 20]; % Radii of obstacles

% Graph Laplacian matrix
L = [ 4, -1, -1, -1, -1;
     -1,  3, -1,  0, -1;
     -1, -1,  3, -1,  0;
     -1,  0, -1,  2,  0;
     -1, -1,  0,  0,  2];

% Initialize variables
x = states(1, :); % x positions
y = states(2, :); % y positions
trajectories = cell(1, N); % Store trajectories for plotting
for i = 1:N
    trajectories{i} = [x(i); y(i)];
end

% Simulation loop
for t_idx = 1:length(times)
    t = times(t_idx);

    % Compute control inputs for each robot
    u_total = zeros(2, N);
    for i = 1:N
        % Formation control using Laplacian
        for j = 1:N
            if L(i, j) ~= 0
                rij = [x(j) - x(i); y(j) - y(i)] - (r_star(:, j) - r_star(:, i));
                u_total(:, i) = u_total(:, i) - kv * L(i, j) * rij;
            end
        end

        % Obstacle avoidance
        for k = 1:size(obstacles, 2)
            ro = obstacles(:, k);
            roi = [ro(1) - x(i); ro(2) - y(i)];
            dist_o = norm(roi);

            if dist_o < Do
                u_total(:, i) = u_total(:, i) - ko * exp(-dist_o^2 / sigma) * (roi / dist_o);
            end
        end
    end

    % Update positions
    for i = 1:N
        if i == 1 % Leader moves upward at constant speed
            x(i) = x(i);
            y(i) = y(i) + v_star(2) * dt;
        else
            x(i) = x(i) + dt * u_total(1, i);
            y(i) = y(i) + dt * u_total(2, i);
        end

        % Store trajectory
        trajectories{i} = [trajectories{i}, [x(i); y(i)]];
    end

    % Plot the robots and obstacles
    clf;
    hold on;
    axis equal;
    xlim([-50, 250]);
    ylim([-100, 550]);

    % Plot obstacles
    for k = 1:size(obstacles, 2)
        viscircles(obstacles(:, k)', obstacle_radii(k), 'Color', 'k', 'LineWidth', 1);
    end

    % Plot trajectories
    for i = 1:N
        plot(trajectories{i}(1, :), trajectories{i}(2, :), 'LineWidth', 1.5);
        plot(x(i), y(i), 'bo', 'MarkerSize', 10, 'MarkerFaceColor', 'b');
    end

    pause(0.1);
end
