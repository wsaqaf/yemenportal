namespace :systemctl do
  namespace :puma do
  end

  namespace :sidekiq do
  end

  namespace :app do
    desc "Start the app"
    task :start do
      on roles(fetch(:systemctl_roles)) do
        sudo(:systemctl, :start, "yemenportal.target")
      end
    end

    desc "Stop the app"
    task :stop do
      on roles(fetch(:systemctl_roles)) do
        sudo(:systemctl, :stop, "yemenportal.target")
      end
    end

    desc "Start the app"
    task :restart do
      on roles(fetch(:systemctl_roles)) do
        sudo(:systemctl, :restart, "yemenportal.target")
      end
    end

    desc "Show status of the app"
    task :status do
      on roles(fetch(:systemctl_roles)) do
        sudo(:systemctl, :status, "yemenportal.target")
      end
    end
  end
end
