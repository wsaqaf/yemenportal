class MainPage::Cell < Application::Cell
  private

  def topics
    model
  end

  def filter_params
    Topics::Filter::Params.new(params)
  end
end
