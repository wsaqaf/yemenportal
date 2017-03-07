class Sources::Form::Cell < Application::Cell
  property :link
  option :categories

  def submit_button
    model.persisted? ? t('source.buttons.edit') : t('source.buttons.create')
  end
end
