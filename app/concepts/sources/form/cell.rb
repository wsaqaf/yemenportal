class Sources::Form::Cell < Application::Cell
  property :link, :state, :approve_state, :whitelisted, :name, :website, :brief_info, :admin_email, :admin_name, :note
  option :categories, :logs

  private

  def submit_button
    if model.persisted?
      approve_state.approved? ? t("source.buttons.update") : "Approve"
    else
      t("source.buttons.create")
    end
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
