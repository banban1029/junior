clear
close all

%% パラメータ
St = 0.1; % サンプリング時間
Ke = 100; % 繰返し回数
N = 5; % エージェント数

x = zeros(N,Ke+1); % x座標の初期化
y = zeros(N,Ke+1); % y座標の初期化
t = zeros(1,Ke+1); % 時間の初期化

%% シミュレーション
for k = 1:Ke+1 % ステップ（時間）についての繰返し
    t(k) = St*(k-1); % 対応する時間
    
    x(:,k) = cos(t(k)+2*pi/N*[0:N-1]'); % x座標の更新 x(エージェント番号，ステップ)
    y(:,k) = sin(t(k)+2*pi/N*[0:N-1]'); % y座標の更新 x(エージェント番号，ステップ)
    % 以下のような書き方もある
    % for i = 1:N % エージェントについての繰返し
    %    x(i,k) = cos(t(k)+2*pi*(i-1)/N); % x座標の更新 x(エージェント番号，ステップ)
    %    y(i,k) = sin(t(k)+2*pi*(i-1)/N); % y座標の更新 y(エージェント番号，ステップ)
    % end

end

%% 結果の表示
figure(1);
for j = 1:6
    k = round((j-1)/5*Ke)+1; % 対応ステップs
    subplot(2,3,j); % サブプロットの場所

    for i = 1:N       
        plot(x(i,k),y(i,k),'o');
        hold on;

    end
    hold off;
    axis([-1,1,-1,1]);
    axis square;
    title(['Time: ', num2str(t(k),'%.2f'), ' s']);

end

% 図の保存
f = gcf;
exportgraphics(f,'multiagent_simulation_2d.jpg','Resolution',300);

%% アニメーションによる表示
figure(2); % 図番号

for k = 1:Ke+1

    for i = 1:N        
        plot(x(i,k),y(i,k),'o'); % エージェントの位置の描画
        hold on; % 描画を消さない

    end

    hold off;
    axis([-1,1,-1,1]); % 図の大きさを指定
    axis square; % 図を正方形に
    title(['Time: ', num2str(t(k),'%.2f'), ' s']); % 経過時間の描画
    pause(0.1); % 動画の各ステップ毎の待ち時間

end