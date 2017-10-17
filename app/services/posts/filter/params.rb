class Posts::Filter::Params
  extend ActiveModel::Naming
  extend Enumerize

  def initialize(raw_params)
    @page = raw_params[:page]
    @q = raw_params[:q]
    @set = raw_params[:set] || :highly_voted
    @time = raw_params[:time] || :daily
  end

  attr_reader :page, :q

  if FeatureToggle.clustering_enabled?
    enumerize :set, in: [:new, :highly_voted, :most_covered], default: :most_covered
  else
    enumerize :set, in: [:new, :highly_voted], default: :highly_voted
  end

  enumerize :time, in: [:daily, :weekly, :monthly, :all_time], default: :daily, predicates: true
end
