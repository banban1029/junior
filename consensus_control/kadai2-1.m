clc;
clear;
close all;

% Simulation parameters
dt = 0.1; % Time step [s]
T = 30; % Total simulation time [s]
times = 0:dt:T;

% Robot parameters
N = 5; % Number of robots
D = 20; % Collision avoidance distance [cm]
Do = 30; % Obstacle sensing range [cm]
Da = 20; % Adaptive range [cm]

% Control gains
kI = 2;
kv = 4;
kvr = 1;
ko = 3000;
sigma = 49;
v_star = [0; 15];

% Formation reference points
r_star = [0, 20; -20/sqrt(3), 0; 20/sqrt(3), 0; -40/sqrt(3), -20; 40/sqrt(3), -20]';

% Initial states (x, y, theta)
states = [105, 16, pi/2;
          88000.5, -3, pi/2;
          111.5, 1000, pi/2;
          77, -34, pi/2;
          -1023.1, -24, pi/2]';

% Obstacle positions (Adjusted to higher positions)
obstacles = [100, 300;
             150, 350;
             200, 400]';
obstacle_radii = [20, 20, 20]; % Radii of obstacles

% Initialize variables
x = states(1, :); % x positions
y = states(2, :); % y positions
theta = states(3, :); % orientations
trajectories = cell(1, N); % Store trajectories for plotting
for i = 1:N
    trajectories{i} = [x(i); y(i)];
end

% Simulation loop
for t_idx = 1:length(times)
    t = times(t_idx);

    % Compute control inputs for each robot
    for i = 1:N
        % Formation control and collision avoidance inputs
        u_formation = zeros(2, 1);
        u_collision = zeros(2, 1);

        % Interaction with neighboring robots
        for j = 1:N
            if i ~= j
                rij = [x(j) - x(i); y(j) - y(i)];
                dist = norm(rij);

                % Collision avoidance potential function
                if dist < 2 * D
                    u_collision = u_collision - (1 / dist + log(dist)) * (rij / dist);
                end
            end
        end

        % Interaction with obstacles
        for k = 1:size(obstacles, 2)
            ro = obstacles(:, k);
            roi = [ro(1) - x(i); ro(2) - y(i)];
            dist_o = norm(roi);

            if dist_o < Do
                % Obstacle avoidance potential function
                u_collision = u_collision - ko * exp(-dist_o^2 / sigma) * (roi / dist_o);
            end
        end

        % Formation control term
        if i > 1
            u_formation = -kvr * ([x(i); y(i)] - [x(1); y(1)] - r_star(:, i));
        end

        % Combine control inputs
        u_total = u_formation + u_collision;

        % Update robot state
        if i == 1 % Move the first robot (blue dot) upward at 15 m/s
            x(i) = x(i);
            y(i) = y(i) + v_star(2) * dt;
        else
            x(i) = x(i) + dt * u_total(1);
            y(i) = y(i) + dt * u_total(2);
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

    % Add markers for specific time points
    if abs(t - 15) < dt / 2
        for i = 1:N
            plot(x(i), y(i), 'mo', 'MarkerSize', 8, 'MarkerFaceColor', 'm');
        end
        text(x(1), y(1), '15s', 'HorizontalAlignment', 'left');
    elseif abs(t - 30) < dt / 2
        for i = 1:N
            plot(x(i), y(i), 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
        end
        text(x(1), y(1), '30s', 'HorizontalAlignment', 'left');
    end

    pause(0.1);
end
