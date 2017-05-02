class Sources::Item::Cell < Application::Cell
  property :link, :id, :user, :state, :name, :website, :brief_info, :admin_email, :admin_name, :note,
    :approve_state, :created_at

  def field_name(field)
    t("source.fields.#{field}")
  end
end
