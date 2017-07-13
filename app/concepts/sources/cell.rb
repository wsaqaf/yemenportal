class Sources::Cell < Application::Cell
  private

  property :link
  option :approve_state, :current_user

  def table_body
    concept("sources/item/cell", collection: model.to_a, current_user: current_user)
  end

  def title
    if approve_state == Source.approve_state.approved
      t("source.title.approved")
    else
      t("source.title.suggested")
    end
  end

  def suggest_button
    path = policy(User).login? ? new_sources_suggest_path : "#"
    button = link_to t("menu.sources.suggest_source"), path, class: "button small float-left"
    button = tooltip_wraper(button) unless policy(User).login?
    button
  end

  def tooltip_wraper(button)
    tolltip_title = t("user.should_login")
    "<span data-tooltip aria-haspopup='true' data-tooltip='' class='has-tip top' \
      title='#{tolltip_title}'>" + button + "</span>"
  end
end
