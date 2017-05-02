class Sources::Item::Cell < Application::Cell
  property :link, :id, :state, :name, :website, :brief_info, :admin_email, :admin_name, :note, :approve_state

  def field_name(field)
    t("source.fields.#{field}")
  end
end
