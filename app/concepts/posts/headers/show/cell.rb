class Posts::Headers::Show::Cell < Application::Cell
  private

  def post
    model
  end

  def logo_srcset
    "#{path_to_image('header_logo_2x.png')} 2x"
  end

  delegate :link, to: :post, prefix: true, allow_nil: true
end
