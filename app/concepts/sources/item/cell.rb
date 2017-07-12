class Sources::Item::Cell < Application::Cell
  option :current_user
  property :link, :id, :user, :state, :name, :website, :brief_info, :admin_email, :admin_name, :note,
    :approve_state, :created_at

  def field_name(field)
    t("source.fields.#{field}")
  end

  def author
    user ? " #{field_name('added_by')} #{user.email}" : ""
  end

  def disabled?
    policy(User).moderator?.blank?
  end
end
