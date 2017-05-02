class Sources::Cell < Application::Cell
  private

  property :link
  option :approve_state

  def table_body
    concept("sources/item/cell", collection: model.to_a)
  end

  def title
    if approve_state == Source.approve_state.approved
      t("source.title.approved")
    else
      t("source.title.suggested")
    end
  end
end
