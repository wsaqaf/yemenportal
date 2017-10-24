class PostsFetcher::FetchedItem
  TITLE_LENGTH_LIMIT = 100
  TITLE_WORDS_SEPARATOR = /\s/

  def initialize(params)
    @params = params
  end

  def link
    params[:link]
  end

  def title
    params[:title] || title_extracted_from_description
  end

  def description
    sanitized_description
  end

  def published_at
    [params[:published_at], Time.zone.now].min
  end

  def image_url
    params[:image_url] || image_url_extracted_from_description
  end

  private

  attr_reader :params

  def sanitized_description
    ActionView::Base.full_sanitizer.sanitize(params[:description])
  end

  def image_url_extracted_from_description
    image_html_element && image_html_element.attributes["src"].value
  end

  def image_html_element
    description_as_html.css("img").first
  end

  def description_as_html
    Nokogiri::HTML.fragment(params[:description])
  end

  def title_extracted_from_description
    description&.truncate(TITLE_LENGTH_LIMIT, separator: TITLE_WORDS_SEPARATOR)
  end
end
