clear
close all

%% パラメータ
St = 0.1; % サンプリング時間
Ke = 100; % 繰返し回数
N = 5; % エージェント数

x = zeros(N,Ke+1); % 状態の初期化
t = zeros(1,Ke+1); % 時間の初期化


%% シミュレーション
for k = 1:Ke+1 % ステップ（時間）についての繰返し
    t(k) = St*(k-1); % 対応する時間
    
    x(:,k) = cos(t(k)+2*pi/N*[0:N-1]'); % 状態の更新 x(エージェント番号，ステップ)
    % 以下のような書き方もある
    % for i = 1:N % エージェントについての繰返し
    %    x(i,k) = cos(t(k)+2*pi*(i-1)/N); % 状態の更新 x(エージェント番号，ステップ)
    %
    % end
end

%% 結果の表示
figure(1); % 図番号

for i = 1:N        
    plot(t,x(i,:)); % エージェントiの状態のプロット
    hold on; % 描画を消さない

end
hold off;
ylabel('Time'); % y軸のラベル

% 図の保存
f = gcf;
exportgraphics(f,'multiagent_simulation_1d.jpg','Resolution',300);