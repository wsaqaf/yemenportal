class Posts::Filter
  def initialize(params)
    @params = Params.new(params)
  end

  def filtered_posts
    filters.reduce(all_posts) do |posts, filter|
      filter.call(posts)
    end
  end

  private

  attr_reader :params

  def all_posts
    ::Post.all
  end

  def filters
    [page_filter, time_filter, sorting_filter, source_filter]
  end

  def page_filter
    ->(posts) { posts.paginate(page: params.page) }
  end

  def time_filter
    if params.all_time?
      ->(posts) { posts }
    else
      ->(posts) { posts.published_later_than(beginning_time_from_params) }
    end
  end

  def beginning_time_from_params
    case params.time.to_sym
    when :hourly
      1.hour.ago
    when :daily
      1.day.ago
    when :weekly
      7.days.ago
    when :monthly
      1.month.ago
    when :annually
      1.year.ago
    end
  end

  def sorting_filter
    case params.set.to_sym
    when :new
      ->(posts) { posts.ordered_by_date }
    when :most_read
      ->(posts) { posts.ordered_by_views_count.ordered_by_date }
    when :highly_voted
      ->(posts) { posts.ordered_by_voting_result.ordered_by_date }
    when :most_covered
      ->(posts) { posts.ordered_by_coverage.ordered_by_voting_result.ordered_by_date }
    end
  end

  def source_filter
    if params.sources.present?
      ->(posts) { posts.source_posts(params.sources) }
    else
      ->(posts) { posts }
    end
  end
end
