class Sources::Form::Cell < Application::Cell
  property :link, :state
  option :categories

  private

  def submit_button
    model.persisted? ? t("source.buttons.update") : t("source.buttons.create")
  end

  def error_message
    t("source.error.#{state}") unless state.valid?
  end
end
