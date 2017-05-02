class Sources::Form::Cell < Application::Cell
  property :link, :state
  option :categories, :logs, :whitelisted, :name, :website, :brief_info, :admin_email, :admin_name, :note

  private

  def submit_button
    model.persisted? ? t("source.buttons.update") : t("source.buttons.create")
  end

  def error_message
    t("source.error.#{state}") unless state.valid?
  end

  def source_logs
    logs || []
  end

  def log_meassage(log)
    if log.state.valid?
      "#{l log.created_at, format: :logs_date} - #{t('source.logs.success', post_count: log.posts_count)}"
    else
      "#{l log.created_at, format: :logs_date} - #{t('source.logs.failure')}"
    end
  end
end
