class Sources::Item::Cell < Application::Cell
  property :link, :id, :user, :state, :name, :website, :brief_info, :admin_email, :admin_name, :note,
    :approve_state, :created_at

  def field_name(field)
    t("source.fields.#{field}")
  end

  def author
    user ? " #{field_name('added_by')} #{user.email}" : ""
  end

  def delete_path
    source_path(model, method: :delete)
  end
end
